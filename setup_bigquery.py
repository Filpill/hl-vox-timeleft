#!/usr/bin/env python3
"""
BigQuery setup script for HL-VOX-TimeLEFT clickstream tracking.

Creates the dataset and table for clickstream events.

Usage:
    python setup_bigquery.py

Requirements:
    - Google Cloud SDK authenticated (gcloud auth application-default login)
    - Permissions to create datasets/tables in the project
"""

from google.cloud import bigquery
from google.api_core import exceptions


def setup_bigquery_clickstream(
    project_id: str = "checkmate-453316",
    dataset_id: str = "hl_timeleft",
    table_id: str = "clickstream",
    location: str = "US"
):
    """
    Create BigQuery dataset and table for clickstream tracking.

    Args:
        project_id: GCP project ID
        dataset_id: Dataset name
        table_id: Table name
        location: BigQuery dataset location
    """
    print(f"Initializing BigQuery client for project: {project_id}")
    client = bigquery.Client(project=project_id)

    # Create dataset
    dataset_ref = f"{project_id}.{dataset_id}"
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = location
    dataset.description = "HL-VOX-TimeLEFT clickstream analytics data"

    try:
        dataset = client.create_dataset(dataset, exists_ok=True)
        print(f"✓ Dataset {dataset_id} created or already exists")
    except exceptions.Forbidden as e:
        print(f"✗ Error: Permission denied creating dataset. {e}")
        return False
    except Exception as e:
        print(f"✗ Error creating dataset: {e}")
        return False

    # Define table schema
    schema = [
        bigquery.SchemaField("user_id", "STRING", mode="REQUIRED",
                           description="Hashed machine identifier for user tracking"),
        bigquery.SchemaField("session_id", "STRING", mode="REQUIRED",
                           description="UUID identifying the application session"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED",
                           description="Event timestamp (UTC)"),
        bigquery.SchemaField("event_type", "STRING", mode="REQUIRED",
                           description="Type of event (e.g., button_click, timer_start)"),
        bigquery.SchemaField("component", "STRING", mode="REQUIRED",
                           description="UI component that triggered the event"),
        bigquery.SchemaField("metadata", "STRING", mode="NULLABLE",
                           description="Additional event metadata (JSON string)"),
    ]

    # Create table
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    table = bigquery.Table(table_ref, schema=schema)
    table.description = "Clickstream events from HL-VOX-TimeLEFT application"

    # Set partitioning by day on timestamp for better query performance
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="timestamp"
    )

    # Set clustering for better performance
    table.clustering_fields = ["user_id", "session_id", "event_type"]

    try:
        table = client.create_table(table, exists_ok=True)
        print(f"✓ Table {table_id} created or already exists")
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        return False

    # Print table details
    print("\n" + "="*60)
    print("BigQuery Clickstream Setup Complete!")
    print("="*60)
    print(f"Project:  {project_id}")
    print(f"Dataset:  {dataset_id}")
    print(f"Table:    {table_id}")
    print(f"Location: {location}")
    print(f"Full ID:  {table_ref}")
    print("="*60)

    print("\nTable Schema:")
    for field in schema:
        print(f"  - {field.name:12} {field.field_type:12} {field.mode:10} {field.description}")

    print("\nFeatures:")
    print("  - Time partitioning by day (timestamp field)")
    print("  - Clustered by user_id, session_id, and event_type")
    print("  - Machine-level user tracking (hashed for privacy)")
    print("  - Session tracking via UUID")
    print("  - Optimized for analytics queries")

    print("\n✓ Setup complete! You can now run the application.")
    print("  Events will be tracked to:", table_ref)

    return True


if __name__ == "__main__":
    import sys

    print("="*60)
    print("HL-VOX-TimeLEFT BigQuery Setup")
    print("="*60)
    print()

    # Check if user wants to customize settings
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print("Usage: python setup_bigquery.py [PROJECT_ID] [DATASET_ID] [TABLE_ID]")
        print()
        print("Defaults:")
        print("  PROJECT_ID  = checkmate-453316")
        print("  DATASET_ID  = hl_timeleft")
        print("  TABLE_ID    = clickstream")
        print()
        sys.exit(0)

    # Parse command line arguments
    project_id = sys.argv[1] if len(sys.argv) > 1 else "checkmate-453316"
    dataset_id = sys.argv[2] if len(sys.argv) > 2 else "hl_timeleft"
    table_id = sys.argv[3] if len(sys.argv) > 3 else "clickstream"

    try:
        success = setup_bigquery_clickstream(project_id, dataset_id, table_id)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure you're authenticated: gcloud auth application-default login")
        print("  2. Check you have permissions in the GCP project")
        print("  3. Verify the project ID is correct")
        sys.exit(1)
