# Clickstream Tracking Documentation

## Overview

The HL-VOX-TimeLEFT application includes BigQuery-based clickstream tracking to capture user interactions with the UI. All button clicks and interactions are tracked asynchronously with automatic batching and graceful shutdown handling.

## Architecture

### Components

**ClickstreamTracker** (`libs/clickstream_tracker.py`)
- Manages event collection and BigQuery insertion
- Batches events (default: 10 per batch)
- Background thread for async processing
- Graceful shutdown with data flush via `atexit`

**Session Tracking**
- Each application instance generates a unique `session_id` (UUID)
- All events in a session share the same `session_id`
- Enables session-based analytics

### Event Schema

```python
{
    "session_id": str,      # UUID for this app session
    "timestamp": str,       # UTC timestamp (ISO 8601)
    "event_type": str,      # e.g., "button_click", "weapon_select", "app_start"
    "component": str,       # UI component name
    "metadata": str|null    # Additional context (JSON string)
}
```

## Setup

### 1. Install Dependencies

```bash
uv sync  # Installs google-cloud-bigquery
```

### 2. Authenticate with Google Cloud

```bash
# Application Default Credentials
gcloud auth application-default login

# Or use a service account
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### 3. Create BigQuery Dataset and Table

Run the setup script:

```bash
python setup_bigquery.py
```

This creates:
- **Dataset**: `experiment-476518.hl_timeleft`
- **Table**: `clickstream`
- **Partitioning**: Daily partitions by timestamp
- **Clustering**: By session_id, event_type, component

### Schema Details

| Field | Type | Mode | Description |
|-------|------|------|-------------|
| `session_id` | STRING | REQUIRED | UUID identifying the application session |
| `timestamp` | TIMESTAMP | REQUIRED | Event timestamp (UTC) |
| `event_type` | STRING | REQUIRED | Type of event (e.g., button_click, timer_start) |
| `component` | STRING | REQUIRED | UI component that triggered the event |
| `metadata` | STRING | NULLABLE | Additional event metadata (JSON string) |

## Configuration

Edit `libs/config.py`:

```python
# Enable/disable tracking
CLICKSTREAM_ENABLED = True  # Set to False to disable

# BigQuery settings
CLICKSTREAM_PROJECT_ID = "experiment-476518"
CLICKSTREAM_DATASET_ID = "hl_timeleft"
CLICKSTREAM_TABLE_ID = "clickstream"
CLICKSTREAM_BATCH_SIZE = 10  # Events per batch
```

## Tracked Events

### Button Clicks

| Component | Event Type | Metadata |
|-----------|------------|----------|
| `start_button` | `button_click` | `{"time_input": "HH:MM:SS"}` |
| `pause_button` | `button_click` | `{"is_paused": true/false}` |
| `reset_button` | `button_click` | None |
| `timeleft_button` | `button_click` | `{"remaining_time": "HH:MM:SS"}` |
| `shoot_gun_button` | `button_click` | `{"weapon": "glock18"}` |
| `change_background_button` | `button_click` | None |

### Other Events

| Component | Event Type | Metadata |
|-----------|------------|----------|
| `weapon_dropdown` | `weapon_select` | `{"weapon": "m4a1"}` |
| `application` | `app_start` | None |

## How It Works

### Event Flow

```
User clicks button
    ↓
UIManager callback
    ↓
clickstream_tracker.track_event()
    ↓
Add to in-memory queue
    ↓
Background thread
    ↓
Batch 10 events
    ↓
Insert to BigQuery (async)
```

### Batching

- Events are queued in-memory
- Background thread processes queue
- Inserts occur when batch reaches 10 events
- On shutdown, all remaining events are flushed

### Graceful Shutdown

When the application exits:
1. `atexit` handler triggers
2. Remaining queue events are collected
3. Final batch is inserted to BigQuery
4. Background thread waits up to 5 seconds to complete

## Querying Data

### Example Queries

**Count clicks by component:**
```sql
SELECT
    component,
    COUNT(*) as click_count
FROM `experiment-476518.hl_timeleft.clickstream`
WHERE event_type = 'button_click'
GROUP BY component
ORDER BY click_count DESC;
```

**Session activity analysis:**
```sql
SELECT
    session_id,
    MIN(timestamp) as session_start,
    MAX(timestamp) as session_end,
    TIMESTAMP_DIFF(MAX(timestamp), MIN(timestamp), SECOND) as session_duration_sec,
    COUNT(*) as total_events
FROM `experiment-476518.hl_timeleft.clickstream`
GROUP BY session_id
ORDER BY session_start DESC;
```

**Weapon popularity:**
```sql
SELECT
    JSON_EXTRACT_SCALAR(metadata, '$.weapon') as weapon,
    COUNT(*) as usage_count
FROM `experiment-476518.hl_timeleft.clickstream`
WHERE component IN ('shoot_gun_button', 'weapon_dropdown')
    AND metadata IS NOT NULL
GROUP BY weapon
ORDER BY usage_count DESC;
```

**Hourly event distribution:**
```sql
SELECT
    EXTRACT(HOUR FROM timestamp) as hour,
    COUNT(*) as event_count
FROM `experiment-476518.hl_timeleft.clickstream`
WHERE DATE(timestamp) = CURRENT_DATE()
GROUP BY hour
ORDER BY hour;
```

## Performance

### Optimizations

- **Time Partitioning**: Daily partitions reduce query costs
- **Clustering**: session_id, event_type, component for faster filters
- **Async Processing**: No UI blocking
- **Batching**: Reduces BigQuery API calls
- **Background Thread**: Daemon thread for non-blocking operation

### Costs

BigQuery pricing (approximate):
- **Storage**: $0.02/GB/month (compressed, partitioned)
- **Inserts**: Free (streaming inserts < 1GB/day)
- **Queries**: $6.25/TB scanned

Estimated monthly cost for moderate usage: **< $1**

## Troubleshooting

### Tracker Fails to Initialize

**Symptom**: Warning message on startup

```
Warning: Failed to initialize BigQuery clickstream tracker: ...
```

**Solutions**:
1. Check authentication: `gcloud auth application-default login`
2. Verify project ID in `libs/config.py`
3. Run setup script: `python setup_bigquery.py`
4. Check IAM permissions (need BigQuery Data Editor role)

### Events Not Appearing

**Check tracker status** (add to code temporarily):
```python
stats = app.clickstream_tracker.get_stats()
print(f"Queue: {stats['queue_size']}, Buffer: {stats['buffer_size']}")
```

**Common issues**:
- Batching delay (wait for 10 events or app exit)
- Tracking disabled (`CLICKSTREAM_ENABLED = False`)
- Table doesn't exist (run setup script)

### Table Not Found Error

```
Error: BigQuery table experiment-476518.hl_timeleft.clickstream not found
```

**Solution**: Run setup script
```bash
python setup_bigquery.py
```

## Disable Tracking

To completely disable clickstream tracking:

**Option 1**: Edit `libs/config.py`
```python
CLICKSTREAM_ENABLED = False
```

**Option 2**: Environment variable (future enhancement)
```bash
export HL_VOX_CLICKSTREAM_ENABLED=false
```

## Privacy Considerations

**Data Collected**:
- Session ID (random UUID, not linked to user identity)
- Button clicks and UI interactions
- Timestamps
- Timer values and weapon selections

**Not Collected**:
- User identity
- IP addresses
- System information
- Personal data

**Data Retention**: Configure BigQuery table expiration if needed:
```bash
bq update --time_partitioning_expiration 2592000 \
    experiment-476518:hl_timeleft.clickstream
```
(30 days = 2592000 seconds)

## Advanced Usage

### Custom Event Tracking

Add custom events anywhere in code:

```python
# In any class with access to clickstream_tracker
self.clickstream_tracker.track_event(
    event_type="custom_action",
    component="my_component",
    metadata={"key": "value"}
)
```

### Export to Other Formats

BigQuery can export to:
- Google Cloud Storage (CSV, JSON, Avro)
- Data Studio for dashboards
- Python/pandas for analysis
- Other databases via Dataflow

Example export:
```bash
bq extract \
    --destination_format=CSV \
    experiment-476518:hl_timeleft.clickstream \
    gs://my-bucket/clickstream-*.csv
```

## Testing

### Manual Test

1. Run application
2. Click several buttons
3. Wait for 10 clicks or exit app
4. Query BigQuery:

```sql
SELECT *
FROM `experiment-476518.hl_timeleft.clickstream`
ORDER BY timestamp DESC
LIMIT 20;
```

### Verify Session ID

```sql
SELECT DISTINCT session_id, COUNT(*) as events
FROM `experiment-476518.hl_timeleft.clickstream`
GROUP BY session_id
ORDER BY MAX(timestamp) DESC;
```

## Future Enhancements

- [ ] Environment variable configuration
- [ ] Local SQLite fallback (offline mode)
- [ ] Real-time event streaming
- [ ] Pre-built dashboard templates
- [ ] A/B testing support
- [ ] Error event tracking
- [ ] Performance metrics (timer accuracy, audio latency)
