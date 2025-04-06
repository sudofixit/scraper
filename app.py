import streamlit as st
import asyncio
import pandas as pd
import os
import sys
from dotenv import set_key
import scraper

# ✅ Set proper event loop policy for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title="CUD Offerings Scraper", layout="wide")
st.title("🎓 CUD Course Offerings Scraper")

# 1. Form for login input and term
with st.form("login_form"):
    st.subheader("🔐 Enter Your Credentials")
    user_id = st.text_input("Student ID", placeholder="e.g., 20240001234")
    password = st.text_input("Password", type="password")

    # ✅ Full Term dropdown options (based on the image)
    term_options = {
        "FA 2025-26": "75",
        "SU 1 2024-25": "73",
        "SP 2024-25": "72",
        "FA 2024-25": "71",
        "SU 2 2023-24": "70",
        "SU 1 2023-24": "75",
        "SP 2023-24": "74",
        "FA 2023-24": "73",
        "SU 2 2022-23": "72",
        "SU 1 2022-23": "71",
        "SP 2022-23": "70",
        "FA 2022-23": "69",
        "SU 2 2021-22": "68",
        "SU 1 2021-22": "67",
        "SP 2021-22": "66"
    }

    term_name = st.selectbox("📅 Select Term", list(term_options.keys()))
    submitted = st.form_submit_button("Start Scraping")

# Update credentials and term in .env
def update_env(id_val, pass_val, term_val):
    set_key(".env", "ID", id_val)
    set_key(".env", "PASSWORD", pass_val)
    set_key(".env", "TERM", term_val)

# 2. Run scrape if form is submitted
if submitted:
    if user_id.strip() and password.strip():
        selected_term_value = term_options[term_name]
        update_env(user_id.strip(), password.strip(), selected_term_value)
        st.success("✅ Credentials and term saved!")

        with st.spinner("⏳ Logging in and scraping..."):
            try:
                result = asyncio.run(scraper.main())

                if result == "invalid":
                    st.error("❌ Invalid credentials. Please check your Student ID and Password.")
                elif result == "error":
                    st.error("❌ Unexpected error occurred during scraping.")
                else:
                    st.success("✅ Scraping complete! File saved as `offerings.csv`")
                    df = pd.read_csv("offerings.csv")
                    st.session_state["scraped_df"] = df
            except Exception as e:
                st.error(f"❌ Error occurred:\n\n{e}")
    else:
        st.warning("⚠️ Please enter both ID and Password.")

# 3. Show data and filters if scraping is done
if "scraped_df" in st.session_state:
    df = st.session_state["scraped_df"]

    st.subheader("📋 Scraped Data")

    df["Instructor"] = df["Instructor"].astype(str).str.strip()
    professors = ["All"] + sorted(df["Instructor"].dropna().unique().tolist())
    selected_prof = st.selectbox("🎓 Filter by Professor", professors)

    if selected_prof != "All":
        df = df[df["Instructor"].str.strip() == selected_prof.strip()]

    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="📥 Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="offerings.csv",
        mime="text/csv"
    )
