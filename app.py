import streamlit as st
import asyncio
import pandas as pd
import os
from dotenv import set_key
import scraper
import sys

# 🛠 Set proper event loop policy for Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

st.set_page_config(page_title="CUD Offerings Scraper", layout="wide")

st.title("🎓 CUD Course Offerings Scraper")

# 1. User login input
with st.form("login_form"):
    st.subheader("🔐 Enter Your Credentials")
    user_id = st.text_input("Student ID", placeholder="e.g., 123456")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Start Scraping")

# Update credentials in .env
def update_env(id_val, pass_val):
    set_key(".env", "ID", id_val)
    set_key(".env", "PASSWORD", pass_val)

# 2. Run scraper and show output
if submitted:
    if user_id and password:
        update_env(user_id, password)
        st.success("✅ Credentials saved!")

        with st.spinner("⏳ Scraping in progress..."):
            try:
                asyncio.run(scraper.main())
                st.success("✅ Scraping complete! File saved as `offerings.csv`")

                # 3. Load and display table
                df = pd.read_csv("offerings.csv")
                st.subheader("📋 Scraped Data")
                st.dataframe(df, use_container_width=True)

                # 4. CSV Download
                st.download_button(
                    label="📥 Download CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name="offerings.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"❌ Error occurred:\n\n{e}")
    else:
        st.warning("⚠️ Please enter both ID and Password to proceed.")
