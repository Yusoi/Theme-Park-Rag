"""
WonderWorld AI Assistant — Pipeline (SOLUTIONS)

Complete working pipeline with all 5 lessons implemented.
"""

import os
import re
import duckdb
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "wonderworld.db")

# --------------------------------------------------------------------------- #
# LLM setup
# --------------------------------------------------------------------------- #

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4.1-mini"),
    api_key=os.getenv("LITELLM_API_KEY"),
    base_url=os.getenv("LITELLM_API_BASE"),
)

# --------------------------------------------------------------------------- #
# Lesson 1: System prompt
# --------------------------------------------------------------------------- #

SYSTEM_PROMPT = """You are the WonderWorld AI Assistant — a smart, friendly analytics copilot for the management team of WonderWorld, a theme park.

## About WonderWorld
- Open from 9:00 to late evening, year-round
- Base capacity: ~2,500 visitors per day (higher on weekends)
- Visitors come in groups (families, friends, or mixed) of 1–5 people
- Peak hours are 12:00–15:00

## Rides (7 total)
- Roller Coaster (most popular, longest queues)
- Ferris Wheel (short queues, family-friendly)
- Haunted House (moderate popularity)
- Water Rapids (moderate-to-high popularity)
- Drop Tower (high popularity, long queues)
- Bumper Cars (short queues, family-friendly)
- Pirate Ship (short-to-moderate queues)

## Restaurants (5 total)
- Pizza Palace, Burger Barn, Sushi Spot, Taco Town, Ice Cream Corner

## Data available
The database tracks every visitor's journey through the park via events:
- `park_entry` / `park_exit` — when visitors enter and leave the park
- `ride_queue_entry` → `ride_entry` → `ride_exit` — the full ride experience (queue time = ride_entry - ride_queue_entry)
- `restaurant_entry` → `restaurant_exit` — dining visits

Each visitor has demographics: age, gender, and a group_id linking them to their travel group.

## Your role
- Help the management team understand park performance: visitor trends, ride popularity, queue times, dining patterns, demographics
- Answer questions using the available data and tools
- When presenting data, be clear and actionable — suggest insights, not just numbers
- You can create charts and visualizations when they help tell the story

## Guardrails
- Only answer questions related to WonderWorld and theme park management
- If asked about unrelated topics (recipes, homework, general knowledge), politely decline and redirect
- Always be transparent about what you know vs. what you're inferring
- When you create a plotly figure using the python interpreter, reference it in your answer using [[figure_name]] so it gets displayed
"""


# --------------------------------------------------------------------------- #
# Lesson 2: DuckDB tool
# --------------------------------------------------------------------------- #

@tool
def query_database(sql: str) -> str:
    """Execute a read-only SQL query against the WonderWorld database.

    Available tables:
    - customers: id (str), age (int), gender (str), group_id (str), date (date)
    - events: id (str), event_type (str), datetime (timestamp), place (str), date (date)
      event_type values: park_entry, park_exit, ride_queue_entry, ride_entry, ride_exit, restaurant_entry, restaurant_exit
    - rides: name (str) — reference table of the 7 ride names
    - restaurants: name (str) — reference table of the 5 restaurant names

    Queue time can be computed by joining ride_queue_entry with ride_entry events
    for the same visitor (id) and ride (place) on the same date.

    Args:
        sql: A read-only SQL query to execute
    """
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        result = con.execute(sql).fetchdf()
        con.close()
        if len(result) > 50:
            return f"Query returned {len(result)} rows. Here are the first 50:\n{result.head(50).to_string()}"
        return result.to_string()
    except Exception as e:
        return f"SQL Error: {e}"


# --------------------------------------------------------------------------- #
# Lesson 3: Custom queue time tool
# --------------------------------------------------------------------------- #

@tool
def get_queue_times(ride_name: str | None = None, time_of_day: str | None = None, day_type: str | None = None) -> str:
    """Get average queue times at WonderWorld rides.

    Queue time is computed as the difference between ride_entry and ride_queue_entry
    for the same visitor at the same ride on the same date.

    Args:
        ride_name: Name of a specific ride (e.g. "Roller Coaster"), or None for all rides
        time_of_day: "morning" (9-13h), "afternoon" (13-17h), "evening" (17-22h), or None for all day
        day_type: "weekday" or "weekend", or None for both
    """
    try:
        con = duckdb.connect(DB_PATH, read_only=True)

        conditions = []
        if ride_name:
            conditions.append(f"q.place = '{ride_name}'")
        if time_of_day:
            hour_ranges = {
                "morning": (9, 13),
                "afternoon": (13, 17),
                "evening": (17, 22),
            }
            if time_of_day in hour_ranges:
                low, high = hour_ranges[time_of_day]
                conditions.append(f"EXTRACT(HOUR FROM q.datetime) >= {low} AND EXTRACT(HOUR FROM q.datetime) < {high}")
        if day_type:
            if day_type == "weekend":
                conditions.append("DAYOFWEEK(q.date) IN (0, 6)")
            elif day_type == "weekday":
                conditions.append("DAYOFWEEK(q.date) NOT IN (0, 6)")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        sql = f"""
        WITH queue_times AS (
            SELECT
                q.place AS ride_name,
                EXTRACT(EPOCH FROM (e.datetime - q.datetime)) / 60.0 AS queue_minutes
            FROM events q
            JOIN events e
                ON q.id = e.id
                AND q.place = e.place
                AND q.date = e.date
                AND q.event_type = 'ride_queue_entry'
                AND e.event_type = 'ride_entry'
            {where_clause}
        )
        SELECT
            ride_name,
            ROUND(AVG(queue_minutes), 1) AS avg_queue_min,
            ROUND(MIN(queue_minutes), 1) AS min_queue_min,
            ROUND(MAX(queue_minutes), 1) AS max_queue_min,
            COUNT(*) AS sample_size
        FROM queue_times
        GROUP BY ride_name
        ORDER BY avg_queue_min DESC
        """

        result = con.execute(sql).fetchdf()
        con.close()

        if result.empty:
            return "No data found for the specified filters."

        summary = "Queue time statistics"
        if ride_name:
            summary += f" for {ride_name}"
        if time_of_day:
            summary += f" during {time_of_day}"
        if day_type:
            summary += f" on {day_type}s"
        summary += f":\n{result.to_string(index=False)}"
        return summary
    except Exception as e:
        return f"Error: {e}"


# --------------------------------------------------------------------------- #
# Lesson 4: Python interpreter for plots
# --------------------------------------------------------------------------- #

figures_store: dict[str, plotly.graph_objects.Figure] = {}


@tool
def run_python(code: str) -> str:
    """Execute Python code to analyze data and create Plotly visualizations.

    The code runs in an environment with pandas (pd), plotly.express (px),
    plotly.graph_objects (go), and duckdb already imported. DB_PATH is available
    to connect to the WonderWorld database.

    To create a chart, build a Plotly figure and store it in the `figures` dict:
        con = duckdb.connect(DB_PATH, read_only=True)
        df = con.execute("SELECT ...").fetchdf()
        con.close()
        fig = px.bar(df, x="ride_name", y="avg_queue")
        figures["my_chart"] = fig

    Then reference it in your text response as [[my_chart]] and it will be
    rendered in the chat.

    Args:
        code: Python code to execute
    """
    namespace = {
        "pd": pd,
        "px": px,
        "go": go,
        "duckdb": duckdb,
        "DB_PATH": DB_PATH,
        "figures": figures_store,
    }
    try:
        exec(code, namespace)
        created_figs = [k for k in figures_store.keys()]
        if created_figs:
            return f"Code executed successfully. Created figures: {', '.join(created_figs)}"
        return "Code executed successfully."
    except Exception as e:
        return f"Python Error: {e}"


# --------------------------------------------------------------------------- #
# Lesson 5: Web search tool
# --------------------------------------------------------------------------- #

from langchain_community.tools import DuckDuckGoSearchRun

web_search = DuckDuckGoSearchRun(
    name="web_search",
    description="Search the web for information. Use this to find data about other theme parks, industry benchmarks, or any external information not available in the WonderWorld database.",
)


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #

def get_tools() -> list:
    """Return the list of tools available to the LLM."""
    return [query_database, get_queue_times, run_python, web_search]


def run_pipeline(user_message: str, chat_history: list[dict]) -> list[str | plotly.graph_objects.Figure]:
    """
    Main pipeline: takes a user message and chat history, returns a list of
    response items (strings and/or Plotly figures).
    """
    figures_store.clear()

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_message))

    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)

    response = llm_with_tools.invoke(messages)

    if hasattr(response, "tool_calls") and response.tool_calls:
        return _run_agent_loop(messages, tools, response)

    return _parse_response(response.content)


def _run_agent_loop(messages, tools, first_response, max_iterations=10):
    """Run the tool-calling agent loop until the LLM stops calling tools."""
    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)

    messages = list(messages)
    response = first_response

    for _ in range(max_iterations):
        messages.append(response)

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            tool_fn = tools_by_name.get(tool_call["name"])
            if tool_fn:
                result = tool_fn.invoke(tool_call["args"])
                messages.append(
                    ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                )
            else:
                messages.append(
                    ToolMessage(
                        content=f"Error: tool '{tool_call['name']}' not found.",
                        tool_call_id=tool_call["id"],
                    )
                )

        response = llm_with_tools.invoke(messages)

    return _parse_response(response.content)


def _parse_response(content: str) -> list[str | plotly.graph_objects.Figure]:
    """Parse a response string, replacing [[figure_name]] with actual Plotly figures."""
    parts = re.split(r"\[\[(\w+)\]\]", content)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            stripped = part.strip()
            if stripped:
                result.append(stripped)
        else:
            fig = figures_store.get(part)
            if fig:
                result.append(fig)
            else:
                result.append(f"[Figure '{part}' not found]")

    return result if result else [content]
