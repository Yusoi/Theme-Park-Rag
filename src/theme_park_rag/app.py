"""
WonderWorld AI Assistant — Main Streamlit App

Run with: uv run streamlit run src/theme_park_rag/app.py
"""

import streamlit as st

from theme_park_rag.pages.ai_assistant import ai_assistant
from theme_park_rag.pages.dataset_overview import dataset_overview
from theme_park_rag.pages.extra_mile import extra_mile
from theme_park_rag.pages.lesson_1_system_prompt import lesson_1_system_prompt
from theme_park_rag.pages.lesson_2_data_access import lesson_2_data_access
from theme_park_rag.pages.lesson_3_custom_tools import lesson_3_custom_tools
from theme_park_rag.pages.lesson_4_visualizations import lesson_4_visualizations
from theme_park_rag.pages.lesson_5_web_search import lesson_5_web_search

pages = [
    st.Page(ai_assistant, title="AI Assistant"),
    st.Page(dataset_overview, title="Dataset Overview"),
    st.Page(lesson_1_system_prompt, title="Lesson 1: System Prompt"),
    st.Page(lesson_2_data_access, title="Lesson 2: Data Access"),
    st.Page(lesson_3_custom_tools, title="Lesson 3: Custom Tools"),
    st.Page(lesson_4_visualizations, title="Lesson 4: Visualizations"),
    st.Page(lesson_5_web_search, title="Lesson 5: Web Search"),
    st.Page(extra_mile, title="Going the Extra Mile"),
]

pg = st.navigation(pages)
pg.run()
