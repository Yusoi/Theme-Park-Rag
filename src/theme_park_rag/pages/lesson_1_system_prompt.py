import streamlit as st


def lesson_1_system_prompt():

    st.title("📝 Lesson 1: LLMs are all about context")

    st.markdown("""
    ## Goal

    Add a **system message** to the pipeline so the agent knows who it is, what WonderWorld is, and what it should (and shouldn't) answer.

    ## The problem

    Right now the pipeline sends the user's message directly to the LLM with no context. Try asking:
    - *"What rides does WonderWorld have?"* — the model has no idea
    - *"Give me a cake recipe"* — it will happily comply

    ## What to do

    Open `src/theme_park_rag/skeleton/pipeline.py` and find the `run_pipeline` function. Look for the TODO comment about adding a system message.

    ### Hint 1: SystemMessage

    LangChain uses message objects. A system message looks like this:

    ```python
    from langchain_core.messages import SystemMessage

    messages = [
        SystemMessage(content="You are a helpful assistant for ..."),
        HumanMessage(content=user_message),
    ]
    ```

    The system message goes **first** in the messages list, before any history or user messages.

    ### Hint 2: What to include in the system prompt

    Your system prompt should cover:
    1. **Identity** — who the agent is ("You are the WonderWorld AI Assistant...")
    2. **Park knowledge** — rides (Roller Coaster, Ferris Wheel, Haunted House, Water Rapids, Drop Tower, Bumper Cars, Pirate Ship), restaurants (Pizza Palace, Burger Barn, Sushi Spot, Taco Town, Ice Cream Corner), peak hours (12–15h)
    3. **Role** — what kind of questions it should help with (park analytics, management decisions)
    4. **Guardrails** — what topics to decline (recipes, homework, anything non-park-related)

    ### Hint 3: A starting template

    ```python
    SYSTEM_PROMPT = \"\"\"You are the WonderWorld AI Assistant — a smart, friendly
    analytics copilot for the management team of WonderWorld theme park.

    ## About WonderWorld
    - Open from 9:00 to late evening, year-round
    - Base capacity: ~2,500 visitors per day (higher on weekends)
    - Peak hours: 12:00–15:00

    ## Rides
    - Roller Coaster, Ferris Wheel, Haunted House, Water Rapids,
    Drop Tower, Bumper Cars, Pirate Ship

    ## Restaurants
    - Pizza Palace, Burger Barn, Sushi Spot, Taco Town, Ice Cream Corner

    ## Guardrails
    - Only answer questions about WonderWorld and theme park management
    - Politely decline unrelated requests
    \"\"\"
    ```

    ## Test it

    After adding your system prompt, restart the app and try:
    - *"What are you?"* → should identify itself as WonderWorld's assistant
    - *"What rides does the park have?"* → should list the 7 rides
    - *"What's a good chocolate cake recipe?"* → should politely decline
    - *"Can kids go on the Drop Tower?"* → should answer based on park knowledge
    """)
