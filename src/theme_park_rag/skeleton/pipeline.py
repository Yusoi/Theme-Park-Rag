"""
WonderWorld AI Assistant — Pipeline

This is the main pipeline that receives a user message and returns a list of
response items (strings or plotly figures) to display in the Streamlit chat.

You will progressively enhance this pipeline across 5 lessons.
"""

import os
import duckdb
import plotly
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
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
# Lesson 2: DuckDB tool
# --------------------------------------------------------------------------- #
# TODO: Create a tool that takes an SQL query string and runs it against the
# WonderWorld DuckDB database, returning the results as a string.
#
# Hint: use the @tool decorator from langchain_core.tools
# The database has these tables:
#   - customers: id, age, gender, group_id, date
#   - events: id, event_type, datetime, place, date
#     event_type values: park_entry, park_exit, ride_queue_entry, ride_entry,
#                        ride_exit, restaurant_entry, restaurant_exit
#   - rides: name (reference table of ride names)
#   - restaurants: name (reference table of restaurant names)
#
# Use duckdb.connect(DB_PATH, read_only=True) to open a connection.


# --------------------------------------------------------------------------- #
# Lesson 3: Custom queue time tool
# --------------------------------------------------------------------------- #
# TODO: Create a dedicated tool that returns average queue times.
# Queue time = time between ride_queue_entry and ride_entry for the same
# visitor (id) at the same ride (place), on the same date.
#
# It should accept optional parameters:
#   - ride_name (str | None): filter by ride, or None for whole park
#   - time_of_day (str | None): "morning" (9-13), "afternoon" (13-17),
#                                "evening" (17-22), or None for all day
#   - day_type (str | None): "weekday" or "weekend", or None for both
#
# This is more robust than letting the LLM write arbitrary SQL.


# --------------------------------------------------------------------------- #
# Lesson 4: Python interpreter for plots
# --------------------------------------------------------------------------- #
# TODO: Create a tool that executes Python code and can produce Plotly figures.
# The tool should:
#   1. Execute the code string in a namespace that has pandas, plotly, and
#      duckdb available (plus DB_PATH so code can query the database)
#   2. Store any Plotly figures created in a shared dictionary (figures_store)
#   3. Return a confirmation message with the figure names
#
# The chat interface will parse [[figure_name]] in the response and replace
# them with the actual Plotly figures.

figures_store: dict[str, plotly.graph_objects.Figure] = {}


# --------------------------------------------------------------------------- #
# Lesson 5: Web search tool
# --------------------------------------------------------------------------- #
# TODO: Add a web search tool so the agent can look up information online.
# Hint: langchain_community has DuckDuckGoSearchRun


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #

def get_tools() -> list:
    """Return the list of tools available to the LLM."""
    tools = []
    # TODO (Lesson 2+): append your tools here as you build them
    return tools


def run_pipeline(user_message: str, chat_history: list[dict]) -> list[str | plotly.graph_objects.Figure]:
    """
    Main pipeline: takes a user message and chat history, returns a list of
    response items (strings and/or Plotly figures).

    Args:
        user_message: The user's latest message
        chat_history: List of {"role": "user"|"assistant", "content": str}

    Returns:
        List of strings and/or Plotly Figure objects to display
    """
    # Clear the figures store for each new message
    figures_store.clear()

    # Build the messages list
    messages = []

    # TODO (Lesson 1): Add a system message here that gives the agent its
    # identity, knowledge about WonderWorld, and guardrails.
    # For now, we just send the raw user message with no system prompt.

    # Add chat history
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    # Add current user message
    messages.append(HumanMessage(content=user_message))

    # Get available tools
    tools = get_tools()

    # Invoke the LLM (with or without tools)
    if tools:
        llm_with_tools = llm.bind_tools(tools)
    else:
        llm_with_tools = llm

    # Simple single-turn call (no tool execution loop yet)
    response = llm_with_tools.invoke(messages)

    # If the response has tool calls, we need an agent loop
    if hasattr(response, "tool_calls") and response.tool_calls:
        return _run_agent_loop(messages, tools, response)

    # Parse the response for [[figure_name]] references
    return _parse_response(response.content)


def _run_agent_loop(messages, tools, first_response, max_iterations=10):
    """Run the tool-calling agent loop until the LLM stops calling tools."""
    from langchain_core.messages import ToolMessage

    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)

    messages = list(messages)  # copy
    response = first_response

    for _ in range(max_iterations):
        # Add the assistant's response to the conversation
        messages.append(response)

        if not response.tool_calls:
            break

        # Execute each tool call
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

        # Call the LLM again with the tool results
        response = llm_with_tools.invoke(messages)

    return _parse_response(response.content)


def _parse_response(content: str) -> list[str | plotly.graph_objects.Figure]:
    """Parse a response string, replacing [[figure_name]] with actual Plotly figures."""
    import re

    parts = re.split(r"\[\[(\w+)\]\]", content)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Text part
            stripped = part.strip()
            if stripped:
                result.append(stripped)
        else:
            # Figure reference
            fig = figures_store.get(part)
            if fig:
                result.append(fig)
            else:
                result.append(f"[Figure '{part}' not found]")

    return result if result else [content]
