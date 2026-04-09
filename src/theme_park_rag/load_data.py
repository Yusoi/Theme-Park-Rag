"""Load partitioned parquet data into a DuckDB database for the workshop."""

import os
import duckdb

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
PARQUET_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
DB_PATH = os.path.join(DATA_DIR, "wonderworld.db")


def load_parquet_to_duckdb(force: bool = False):
    """Read Hive-partitioned parquet files and load them into a single DuckDB database."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DB_PATH) and not force:
        print(f"Database already exists at {DB_PATH}. Use force=True to rebuild.")
        return DB_PATH

    customers_path = os.path.join(PARQUET_DIR, "customers", "**", "*.parquet")
    events_path = os.path.join(PARQUET_DIR, "events", "**", "*.parquet")

    con = duckdb.connect(DB_PATH)

    print("Loading customers...")
    con.execute(f"""
        CREATE OR REPLACE TABLE customers AS
        SELECT * FROM read_parquet('{customers_path.replace(os.sep, '/')}', hive_partitioning=true)
    """)
    count = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    print(f"  customers: {count} rows")

    print("Loading events...")
    con.execute(f"""
        CREATE OR REPLACE TABLE events AS
        SELECT * FROM read_parquet('{events_path.replace(os.sep, '/')}', hive_partitioning=true)
    """)
    count = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    print(f"  events: {count} rows")

    # Create a rides reference table
    print("Creating rides reference table...")
    con.execute("""
        CREATE OR REPLACE TABLE rides AS
        SELECT DISTINCT place as name
        FROM events
        WHERE event_type = 'ride_queue_entry'
        ORDER BY name
    """)

    # Create a restaurants reference table
    print("Creating restaurants reference table...")
    con.execute("""
        CREATE OR REPLACE TABLE restaurants AS
        SELECT DISTINCT place as name
        FROM events
        WHERE event_type = 'restaurant_entry'
        ORDER BY name
    """)

    # Print summaries
    for table in ["customers", "events", "rides", "restaurants"]:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")

    con.close()
    print(f"Database saved to {DB_PATH}")
    return DB_PATH


if __name__ == "__main__":
    load_parquet_to_duckdb(force=True)
