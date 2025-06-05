import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from api.jsearch_api import search_jobs
from utils.semantic_matcher import score_jobs_semantically

st.title("🔍 Step 2: Search and Match Jobs")

with st.form("search_form"):
    title = st.text_input("Job Title", "Mechanical Designer")
    location = st.text_input("Location", "Vancouver, BC")
    pages = st.slider("How many pages to fetch?", 1, 5, 2)
    submitted = st.form_submit_button("Search Jobs")

if submitted:
    with st.spinner("Fetching and ranking jobs..."):
        resume = st.session_state.get("resume_text", "")
        df = search_jobs(title, location, pages)
        df = score_jobs_semantically(df, resume)
        st.session_state.matched_jobs = df
        st.success("Jobs matched and ready!")
        st.switch_page("pages/4_View_Matches.py")
