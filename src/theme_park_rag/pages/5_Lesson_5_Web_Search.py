import streamlit as st

st.set_page_config(page_title="Lesson 5 — Web Search", page_icon="🌐")

st.title("🌐 Lesson 5: Web search for competitive benchmarking")

st.markdown("""
## Goal

Add a **web search tool** so the agent can fetch live information from the internet — enabling competitive analysis and industry benchmarking.

## What to do

LangChain has a built-in DuckDuckGo search tool. You just need to import it and register it.

### Hint 1: Import and create

```python
from langchain_community.tools import DuckDuckGoSearchRun

web_search = DuckDuckGoSearchRun(
    name="web_search",
    description="Search the web for information about other theme parks, "
                "industry benchmarks, or any external data not in WonderWorld's database.",
)
```

### Hint 2: Register it

```python
def get_tools() -> list:
    return [query_database, get_queue_times, run_python, web_search]
```

That's it! The `DuckDuckGoSearchRun` is already a LangChain tool, so it works out of the box with `bind_tools`.

### Hint 3: You may need to install ddgs

If you get an import error, run:
```bash
uv add ddgs
```

## Test it

- *"How do our ticket prices compare to Disneyland Paris?"*
- *"What's the average queue time at Europa-Park's top rides?"*
- *"What new ride technologies are trending in theme parks this year?"*
- *"How does our visitor capacity compare to PortAventura?"*
- *"What strategies do other parks use to reduce queue times?"*

## The big picture

With all 5 lessons complete, you have an agent that can:
1. **Understand context** — knows what it is and what it should do
2. **Query internal data** — runs SQL against real operational data
3. **Use scoped tools** — reliable, purpose-built functions for common queries
4. **Create visualizations** — generates charts on the fly
5. **Access the web** — benchmarks against competitors with live data

This is the pattern behind real-world AI assistants in production.
""")
