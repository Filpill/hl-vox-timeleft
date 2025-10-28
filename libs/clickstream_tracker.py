"""
ClickstreamTracker class for Half-Life VOX TimeLEFT application.
Handles asynchronous clickstream tracking to BigQuery with batching.
"""

import atexit
import threading
import queue
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from google.cloud import bigquery
from google.api_core import exceptions

from libs.machine_id import get_machine_id
from libs.version import __version__


class ClickstreamTracker:
    """
    Manages clickstream event tracking to BigQuery.

    Features:
    - Asynchronous batch inserts (batches of 10)
    - Background thread for processing
    - Graceful shutdown with data flush
    - Automatic retry on transient errors
    """

    def __init__(
        self,
        project_id: str = "experiment-476518",
        dataset_id: str = "hl_timeleft",
        table_id: str = "clickstream",
        batch_size: int = 10,
        enabled: bool = True
    ):
        """
        Initialize the clickstream tracker.

        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
            batch_size: Number of events to batch before inserting
            enabled: Whether tracking is enabled
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.batch_size = batch_size
        self.enabled = enabled

        # Get stable machine identifier
        self.user_id = get_machine_id()

        # Generate unique session ID for this application instance
        self.session_id = str(uuid.uuid4())

        # Get application version
        self.app_version = __version__

        # Event queue for async processing
        self.event_queue = queue.Queue()
        self.batch_buffer = []
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()

        # BigQuery client
        self.client = None
        self.table_ref = None

        if self.enabled:
            try:
                self.client = bigquery.Client(project=project_id)
                self.table_ref = f"{project_id}.{dataset_id}.{table_id}"

                # Start background processing thread
                self.worker_thread = threading.Thread(
                    target=self._process_events,
                    daemon=True
                )
                self.worker_thread.start()

                # Register cleanup handler
                atexit.register(self.shutdown)

            except Exception as e:
                print(f"Warning: Failed to initialize BigQuery clickstream tracker: {e}")
                self.enabled = False

    def track_event(
        self,
        event_type: str,
        component: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Track a clickstream event.

        Args:
            event_type: Type of event (e.g., "button_click", "timer_start")
            component: UI component name (e.g., "start_button", "pause_button")
            metadata: Additional event metadata
        """
        if not self.enabled:
            return

        event = {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "app_version": self.app_version,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "component": component,
            "metadata": str(metadata) if metadata else None
        }

        try:
            self.event_queue.put_nowait(event)
        except queue.Full:
            print("Warning: Event queue full, dropping event")

    def _process_events(self):
        """Background thread worker to process events."""
        while not self.shutdown_event.is_set():
            try:
                # Get event with timeout to allow checking shutdown flag
                event = self.event_queue.get(timeout=0.5)

                with self.lock:
                    self.batch_buffer.append(event)

                    # Insert batch when it reaches batch_size
                    if len(self.batch_buffer) >= self.batch_size:
                        self._insert_batch()

            except queue.Empty:
                # No events, check if we should flush partial batch
                if self.shutdown_event.is_set():
                    break
                continue
            except Exception as e:
                print(f"Error processing event: {e}")

    def _insert_batch(self):
        """Insert current batch to BigQuery."""
        if not self.batch_buffer or not self.client:
            return

        try:
            errors = self.client.insert_rows_json(
                self.table_ref,
                self.batch_buffer,
                retry=bigquery.DEFAULT_RETRY
            )

            if errors:
                print(f"BigQuery insert errors: {errors}")
            else:
                print(f"Successfully inserted {len(self.batch_buffer)} events to BigQuery")

            # Clear buffer after insert (success or failure)
            self.batch_buffer.clear()

        except exceptions.NotFound:
            print(f"Error: BigQuery table {self.table_ref} not found. "
                  f"Run setup_bigquery.py to create it.")
            self.batch_buffer.clear()
        except Exception as e:
            print(f"Error inserting to BigQuery: {e}")
            # Keep buffer to retry on next batch
            if len(self.batch_buffer) > self.batch_size * 3:
                # Drop oldest events if buffer grows too large
                self.batch_buffer = self.batch_buffer[-self.batch_size:]

    def shutdown(self):
        """
        Gracefully shutdown tracker, flushing remaining events.
        Called automatically via atexit.
        """
        if not self.enabled:
            return

        print("Shutting down clickstream tracker...")
        self.shutdown_event.set()

        # Process remaining events in queue
        remaining_events = []
        while not self.event_queue.empty():
            try:
                remaining_events.append(self.event_queue.get_nowait())
            except queue.Empty:
                break

        # Add to batch buffer
        with self.lock:
            self.batch_buffer.extend(remaining_events)

            # Flush final batch
            if self.batch_buffer:
                print(f"Flushing {len(self.batch_buffer)} remaining events...")
                self._insert_batch()

        # Wait for worker thread to finish
        if hasattr(self, 'worker_thread') and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5.0)

        print("Clickstream tracker shutdown complete")

    def get_stats(self) -> Dict[str, int]:
        """
        Get tracker statistics.

        Returns:
            Dictionary with queue size and buffer size
        """
        with self.lock:
            return {
                "queue_size": self.event_queue.qsize(),
                "buffer_size": len(self.batch_buffer)
            }
