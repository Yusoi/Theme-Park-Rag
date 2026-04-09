"""
WonderWorld AI Assistant — Streamlit App

Run with: uv run streamlit run src/theme_park_rag/app.py
"""

import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="WonderWorld AI Assistant", page_icon="🎢", layout="wide")

# Import the pipeline — students edit skeleton/pipeline.py
from theme_park_rag.skeleton.pipeline import run_pipeline

st.title("🎢 WonderWorld AI Assistant")
st.caption("Your theme park analytics copilot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for item in message["content"]:
            if isinstance(item, go.Figure):
                st.plotly_chart(item, use_container_width=True)
            else:
                st.markdown(item)

# Chat input
if prompt := st.chat_input("Ask something about WonderWorld..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build chat history for the pipeline (text only)
    chat_history = []
    for msg in st.session_state.messages[:-1]:  # exclude the current message
        text_parts = [item for item in msg["content"] if isinstance(item, str)]
        chat_history.append({
            "role": msg["role"],
            "content": "\n".join(text_parts),
        })

    # Run the pipeline
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_items = run_pipeline(prompt, chat_history)

        for item in response_items:
            if isinstance(item, go.Figure):
                st.plotly_chart(item, use_container_width=True)
            else:
                st.markdown(item)

    # Store assistant response
    st.session_state.messages.append({"role": "assistant", "content": response_items})
