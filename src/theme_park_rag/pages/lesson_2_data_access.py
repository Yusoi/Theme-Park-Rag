import streamlit as st


def lesson_2_data_access():
    st.title("🗄️ Lesson 2: Enabling the agent with data access")

    st.markdown("""
    ## Goal

    Give the agent the ability to **query the WonderWorld database** using DuckDB, so it can answer questions based on real data instead of guessing.

    ## The problem

    After Lesson 1, the agent knows *about* WonderWorld, but it can't look at any data. Ask *"How many visitors came on January 15th?"* and it will either hallucinate a number or say it doesn't know.

    ## What to do

    In `src/theme_park_rag/skeleton/pipeline.py`:

    1. **Create a tool** using the `@tool` decorator
    2. **Register it** in the `get_tools()` function

    ### Hint 1: The @tool decorator

    ```python
    from langchain_core.tools import tool

    @tool
    def query_database(sql: str) -> str:
        \"\"\"Execute a read-only SQL query against the WonderWorld database.

        Available tables:
        - customers: id (str), age (int), gender (str), group_id (str), date (date)
        - events: id (str), event_type (str), datetime (timestamp), place (str), date (date)
        event_type: park_entry, park_exit, ride_queue_entry, ride_entry,
                    ride_exit, restaurant_entry, restaurant_exit
        - rides: name (str) — reference table of ride names
        - restaurants: name (str) — reference table of restaurant names
        \"\"\"
        # Your implementation here
        pass
    ```

    The docstring matters — it tells the LLM what the tool does and what tables are available.

    ### Hint 2: Using DuckDB

    ```python
    import duckdb

    con = duckdb.connect(DB_PATH, read_only=True)
    result = con.execute(sql).fetchdf()  # returns a pandas DataFrame
    con.close()
    return result.to_string()
    ```

    ### Hint 3: Register the tool

    ```python
    def get_tools() -> list:
        return [query_database]
    ```

    ### Hint 4: Useful query patterns

    Queue time for a ride = time between `ride_queue_entry` and `ride_entry` for the same visitor (`id`) at the same ride (`place`) on the same `date`:

    ```sql
    SELECT
        q.place AS ride,
        AVG(EXTRACT(EPOCH FROM (e.datetime - q.datetime)) / 60.0) AS avg_queue_min
    FROM events q
    JOIN events e ON q.id = e.id AND q.place = e.place AND q.date = e.date
    WHERE q.event_type = 'ride_queue_entry' AND e.event_type = 'ride_entry'
    GROUP BY q.place
    ```

    ## Test it

    - *"How many visitors came on 2025-07-01?"*
    - *"Which ride has the longest average queue time?"*
    - *"What's the most popular restaurant?"*
    - *"Break down visitors by gender for last month."*
    """)
