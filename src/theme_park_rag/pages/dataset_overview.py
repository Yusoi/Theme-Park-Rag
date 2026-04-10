import streamlit as st


def dataset_overview():
    st.title("📊 Dataset Overview: Understanding the Theme Park Data")

    st.markdown("""
    # Dataset Overview

    You are working with a **synthetic event dataset representing visitor behavior in a theme park** over the course of approximately one year.

    The data is organized into two main tables:

    - **`events`** → behavioral event log (fact table)
    - **`customers`** → visitor attributes (dimension table)

    Both are stored as **partitioned Parquet files**, queryable via DuckDB.

    ---

    # Data Model

    ## 1. Events Table (Core Behavioral Data)

    Each row represents a **single event performed by a visitor at a specific point in time**.

    ### Columns

    | Column      | Description |
    |------------|------------|
    | `id`       | Visitor identifier |
    | `event_type` | Type of event (see below) |
    | `datetime` | Timestamp of the event |
    | `place`    | Location where the event occurred |
    | `date`     | Partition column (derived from folder structure) |

    ---

    ## Event Types

    The dataset models **three main activity domains**:

    ### 1. Park lifecycle
    - `park_entry`
    - `park_exit`

    ### 2. Ride lifecycle
    - `ride_queue_entry`
    - `ride_entry`
    - `ride_exit`

    ### 3. Restaurant lifecycle
    - `restaurant_entry`
    - `restaurant_exit`

    ---

    ## Event Semantics

    Events follow **strict temporal and logical consistency**:

    ### Example visitor flow

        → park_entry
        → ride_queue_entry
        → ride_entry
        → ride_exit
        → restaurant_entry
        → restaurant_exit
        → park_exit

    ### Important properties
    - Events are **chronologically ordered per visitor**
    - Ride events occur in valid sequences:
    - queue → entry → exit
    - Visitors may:
    - perform multiple rides
    - eat at restaurants
    - leave and re-enter the park (multiple sessions per day)

    ---

    # 2. Customers Table (Visitor Attributes)

    Each row represents a **unique visitor**.

    ### Columns

    | Column     | Description |
    |-----------|------------|
    | `id`      | Visitor identifier (joins with events) |
    | `age`     | Age of the visitor |
    | `gender`  | Gender category |
    | `group_id`| Group identifier (family, friends, etc.) |

    ---

    ## Behavioral Context

    Visitors are not independent:

    - Visitors are organized into **groups**
    - Groups represent:
    - families
    - friends
    - mixed compositions

    ### Group behavior
    - Most visitors behave similarly within a group
    - ~5% exhibit **independent behavior** (deviations)

    ---

    # Temporal Coverage

    - Data spans **~1 year**
    - Stored as **daily partitions**:

        events/date=YYYY-MM-DD/
        customers/date=YYYY-MM-DD/

    ### Implications
    - Efficient time-based filtering
    - Natural support for:
    - daily trends
    - seasonality
    - weekday vs weekend analysis

    ---

    # Behavioral Realism

    The dataset includes several **realistic dynamics**:

    ## 1. Visitor volume variability
    - Daily visitor counts fluctuate
    - Weekends have higher attendance

    ## 2. Queue dynamics
    - Queue times depend on:
    - ride popularity
    - time of day (peak hours)

    ## 3. Restaurant behavior
    - Eating is probabilistic
    - Strongly influenced by time (lunch/dinner peaks)

    ## 4. Multi-session visits
    - Visitors may:
    - leave the park
    - return later the same day
""")
