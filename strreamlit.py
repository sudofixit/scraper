import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CUD Course Scraper", layout="centered")

st.title("📘 CUD Course Scraper")
st.markdown("Use this tool to log in, scrape course offerings, and explore or download the data easily.")

# --- LOGIN SECTION ---
st.subheader("🔐 Login Credentials")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
headless = st.checkbox("Run in headless mode (no browser window)", value=True)

# --- SCRAPER SETTINGS ---
st.subheader("⚙️ Scraper Settings")
page_limit = st.slider("How many pages to scrape?", min_value=1, max_value=8, value=8)
scrape = st.button("🚀 Scrape Course Offerings")

# Placeholder for CSV file preview
if scrape:
    st.success("Scraping complete! Preview below:")

# --- Search Filters and Data ---
st.subheader("🔍 Search Filters")

if os.path.exists("offerings.csv"):
    df = pd.read_csv("offerings.csv")

    col1, col2 = st.columns(2)
    with col1:
        instructor_filter = st.text_input("Search by Instructor")
    with col2:
        course_filter = st.text_input("Search by Course Name")

    filtered_df = df.copy()
    if instructor_filter:
        filtered_df = filtered_df[filtered_df["Instructor"].str.contains(instructor_filter, case=False, na=False)]
    if course_filter:
        filtered_df = filtered_df[filtered_df["Course Name"].str.contains(course_filter, case=False, na=False)]

    st.markdown("### 📋 Filtered Course Offerings")
    st.dataframe(filtered_df, use_container_width=True)

    st.download_button("📥 Download CSV", filtered_df.to_csv(index=False), "offerings.csv")
else:
    st.info("Run the scraper to view and filter course offerings.")
