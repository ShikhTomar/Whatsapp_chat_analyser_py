import streamlit as st
import Preprocessor, Helper
import matplotlib.pyplot as plt
import plotly.express as px

import seaborn as sns

from Helper import activity_map

# Set page config for a wider layout
st.set_page_config(layout="wide")

st.sidebar.title("Whatsapp Chat Analyser")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = Preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # --- Top Statistics ---
        num_messages, words, num_media_messages, num_links = Helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Media Shared", num_media_messages)
        with col4:
            st.metric("Links Shared", num_links)

        # --Monthly- Timeline ---
        st.title("Monthly Timeline")
        timeline = Helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(timeline['time'], timeline['message'], color='green', linewidth=2)
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        #daily---timeline
        st.title("daily Timeline")
        daily_timeline = Helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='purple', linewidth=2)
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
        #activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Busy Day")
            busy_day = Helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='#fbb1bd',edgecolor='#ff85a1')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.header("Most Busy month")
            busy_month = Helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='#ff99ac',edgecolor='#ff85a1')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        st.title("Weekly Activity Map")
        user_map = Helper.activity_map(selected_user, df)

        # Using a smaller figsize helps the boxes look "fuller" in Streamlit
        fig, ax = plt.subplots(figsize=(12, 6))

        # Use fmt='d' to show integers instead of scientific notation (like 0.100)
        sns.heatmap(user_map, annot=True, cmap='Blues', fmt='g', ax=ax)

        plt.xlabel("Time Period")
        plt.ylabel("Day of the Week")
        st.pyplot(fig)


        # --- Busiest User (Group Level Only) ---
        if selected_user == "Overall":
            st.title("Most Busy Users")
            x, new_df = Helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='#87CEEB', edgecolor='#4682B4')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df, use_container_width=True)

        # --- Word Cloud ---
        st.title("Word Cloud")
        df_wc = Helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        # --- Most Common Words ---
        st.title("Most Common Words")
        most_common_df = Helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color='#FF8C00')
        st.pyplot(fig)

        # --- Emoji Analysis ---
        st.title("Emoji Analysis")
        emoji_df = Helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df, use_container_width=True)

        with col2:
            if not emoji_df.empty:
                # Top 5 for aesthetic look
                top_5 = emoji_df.head(5)
                # Aesthetic Pastel Colors
                colors = ['#ffadad', '#ffd6a5', '#fdffb6', '#caffbf', '#9bfbc0']

                fig, ax = plt.subplots()
                ax.pie(top_5[1], labels=top_5[0], autopct='%1.1f%%', colors=colors, startangle=140)

                # Create the Donut hole for extra aesthetics
                centre_circle = plt.Circle((0, 0), 0.70, fc='white')
                fig.gca().add_artist(centre_circle)

                st.pyplot(fig)
            else:
                st.info("No emojis found in this conversation.")