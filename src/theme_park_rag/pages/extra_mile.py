import random

import streamlit as st


def extra_mile():

    st.title("🏃 Going the Extra Mile")

    st.markdown("""
        This is where you can experiment with your own ideas and push the boundaries of what's possible with your AI assistant. Here are some suggestions to get you started:
        1. **Add more tools**: Integrate additional APIs or databases relevant to theme parks, such as weather data, social media sentiment analysis, or ride maintenance logs.
        2. **Improve the system prompt**: Refine the assistant's instructions to make it more helpful, creative, or aligned with your specific use case.
        3. **Draw from the roulette**: Try implementing one of the features from the roulette wheel below!
    """)

    def spin_roulette():

        features = [
            # Visitor Behavior
            "How many unique visitors enter the park per day?",
            "What is the average number of sessions per visitor?",
            "What percentage of visitors re-enter the park on the same day?",
            "What is the average time spent in the park per session?",
            "What is the distribution of visit durations?",
            "What time of day do most visitors first enter the park?",
            "What is the earliest park entry recorded?",
            "What is the latest park exit recorded?",
            "How many visitors leave the park without using any rides?",
            "What percentage of visitors only enter the park once?",
            # Ride Behavior
            "What are the most popular rides by number of entries?",
            "What is the average number of rides per visitor?",
            "Which rides have the longest average queue times?",
            "What is the average ride duration per ride?",
            "At what times are rides most frequently used?",
            "Which rides are most popular among different age groups?",
            "What percentage of visitors only take one ride?",
            "What is the most common sequence of rides?",
            "How often do visitors repeat the same ride?",
            "Which ride has the highest throughput (entries per hour)?",
            # Queue & Congestion Analysis
            "What is the average queue time per ride?",
            "How does queue time vary during peak hours vs off-peak?",
            "Which rides experience the highest congestion during weekends?",
            "What is the longest queue time recorded?",
            "At what time of day are queues shortest?",
            "How does queue time vary across different days?",
            "Which rides have the most consistent queue times?",
            "What percentage of time do visitors spend waiting in queues?",
            "Are independent visitors experiencing shorter or longer queues?",
            "How does queue time correlate with ride popularity?",
            # Restaurant & Consumption Behavior
            "What percentage of visitors eat at least once?",
            "What is the most popular restaurant?",
            "At what times do most restaurant visits occur?",
            "What is the average duration of a restaurant visit?",
            "How many visitors eat before taking their first ride?",
            "How many visitors eat after completing all rides?",
            "Which age groups are more likely to visit restaurants?",
            "What is the average number of restaurant visits per visitor?",
            "Do visitors who eat spend more time in the park?",
            "Which restaurants are most popular during peak hours?",
            # Demographics & Segmentation
            "What is the distribution of visitors by age group?",
            "How does ride usage vary by gender?",
            "Do families behave differently from friend groups?",
            "Which demographic group spends the most time in the park?",
            "Are younger visitors more likely to ride more attractions?",
            "Do certain demographics prefer specific rides?",
            "How does restaurant usage vary by age?",
            "What is the average group size?",
            "Do larger groups stay longer in the park?",
            "Are independent visitors behaviorally different from group-aligned visitors?",
        ]

        selected_feature = random.choice(features)
        st.markdown(f"🎉 Your roulette result: **{selected_feature}**")

    st.button("Spin the Roulette 🎡", on_click=spin_roulette)
