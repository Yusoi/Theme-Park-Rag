import streamlit as st

st.set_page_config(page_title="Lesson 3 — Custom Tools", page_icon="🔧")

st.title("🔧 Lesson 3: Increasing robustness with tools of limited scope")

st.markdown("""
## Goal

Create a **dedicated tool** for queue time queries. Instead of relying on the LLM to write correct SQL every time, give it a well-defined function with clear parameters.

## Why?

The `query_database` tool is powerful but fragile — the LLM might write wrong SQL, join incorrectly, or misinterpret event types. A scoped tool with named parameters is:
- **More reliable** — the LLM just needs to pick the right arguments
- **Safer** — you control exactly what queries run
- **Easier to test** — it's a normal function

## What to do

Create a `get_queue_times` tool with optional parameters:

### Hint 1: Tool signature

```python
@tool
def get_queue_times(
    ride_name: str | None = None,
    time_of_day: str | None = None,
    day_type: str | None = None,
) -> str:
    \"\"\"Get average queue times at WonderWorld rides.

    Queue time = time between ride_queue_entry and ride_entry for the same
    visitor at the same ride on the same date.

    Args:
        ride_name: Name of a specific ride (e.g. "Roller Coaster"), or None for all rides
        time_of_day: "morning" (9-13h), "afternoon" (13-17h), "evening" (17-22h), or None
        day_type: "weekday" or "weekend", or None for both
    \"\"\"
```

### Hint 2: Computing queue time with a JOIN

```python
sql = \"\"\"
WITH queue_times AS (
    SELECT
        q.place AS ride_name,
        EXTRACT(EPOCH FROM (e.datetime - q.datetime)) / 60.0 AS queue_minutes
    FROM events q
    JOIN events e
        ON q.id = e.id AND q.place = e.place AND q.date = e.date
        AND q.event_type = 'ride_queue_entry'
        AND e.event_type = 'ride_entry'
    {where_clause}
)
SELECT ride_name, ROUND(AVG(queue_minutes), 1) AS avg_queue_min, ...
FROM queue_times
GROUP BY ride_name
\"\"\"
```

### Hint 3: Building filters dynamically

```python
conditions = []
if ride_name:
    conditions.append(f"q.place = '{ride_name}'")
if time_of_day:
    hour_ranges = {"morning": (9, 13), "afternoon": (13, 17), "evening": (17, 22)}
    low, high = hour_ranges[time_of_day]
    conditions.append(f"EXTRACT(HOUR FROM q.datetime) >= {low} AND EXTRACT(HOUR FROM q.datetime) < {high}")

where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
```

### Hint 4: Register it

```python
def get_tools() -> list:
    return [query_database, get_queue_times]
```

## Test it

- *"What's the average queue time across the whole park?"*
- *"How long is the wait for Roller Coaster?"*
- *"Compare morning vs. afternoon queue times for Haunted House."*
- *"Are weekend queues longer than weekday queues?"*
- *"Which ride has the shortest queue in the evening?"*
""")
