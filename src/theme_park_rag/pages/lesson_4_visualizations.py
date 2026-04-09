import streamlit as st


def lesson_4_visualizations():
    st.title("📊 Lesson 4: Creating a better product with visualizations")

    st.markdown("""
    ## Goal

    Add a **Python code interpreter** tool that lets the agent write and execute code to create Plotly visualizations, which get rendered directly in the chat.

    ## How it works

    1. The LLM writes Python code that creates a Plotly figure
    2. The code stores the figure in a shared dictionary: `figures["chart_name"] = fig`
    3. The LLM references it in its text response: `[[chart_name]]`
    4. The chat interface parses `[[chart_name]]` and replaces it with the actual chart

    ## What to do

    ### Hint 1: The tool

    ```python
    @tool
    def run_python(code: str) -> str:
        \"\"\"Execute Python code to analyze data and create Plotly visualizations.

        The code has pandas (pd), plotly.express (px), plotly.graph_objects (go),
        and duckdb available. DB_PATH is available to connect to the database.

        Example:
            con = duckdb.connect(DB_PATH, read_only=True)
            df = con.execute("SELECT ...").fetchdf()
            con.close()
            fig = px.bar(df, x="ride", y="avg_queue")
            figures["queue_chart"] = fig

        Args:
            code: Python code to execute
        \"\"\"
    ```

    ### Hint 2: Implementation using exec

    ```python
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    namespace = {
        "pd": pd,
        "px": px,
        "go": go,
        "duckdb": duckdb,
        "DB_PATH": DB_PATH,
        "figures": figures_store,  # the shared dict defined at module level
    }
    try:
        exec(code, namespace)
        created = [k for k in figures_store.keys()]
        if created:
            return f"Code executed. Created figures: {', '.join(created)}"
        return "Code executed successfully."
    except Exception as e:
        return f"Python Error: {e}"
    ```

    ### Hint 3: The figures_store dict

    This is already defined in the skeleton:
    ```python
    figures_store: dict[str, plotly.graph_objects.Figure] = {}
    ```

    It gets cleared at the start of each `run_pipeline` call. The `_parse_response` function already handles `[[figure_name]]` replacement — you just need to create the tool.

    ### Hint 4: Update the system prompt

    Tell the LLM how to use figures in its responses:
    ```
    When creating charts, store the Plotly figure in the figures dict and reference
    it in your answer as [[figure_name]].
    ```

    ## Test it

    - *"Show me a bar chart of average queue times per ride."*
    - *"Plot daily visitor counts for July."*
    - *"Create a heatmap of ride popularity by hour of the day."*
    - *"Compare restaurant visits across the 5 restaurants as a pie chart."*
    - *"Show the age distribution of visitors as a histogram."*
    """)
