import streamlit as st
import pandas as pd

st.title("📊 Step 3: View Job Matches")

df = st.session_state.get("matched_jobs")

if df is None:
    st.warning("No job matches found. Go back and search first.")
    st.page_link("pages/3_Search_Jobs.py", label="← Back to Job Search")
else:
    score_range = st.slider("Filter by Score", 0.0, 1.0, (0.4, 1.0), step=0.01)
    search = st.text_input("Search title or company")

    filtered = df[df["score"].between(*score_range)]

    if search:
        filtered = filtered[
            filtered["title"].str.contains(search, case=False, na=False) |
            filtered["company"].str.contains(search, case=False, na=False)
        ]

    st.write(f"Showing {len(filtered)} job(s):")

    for _, row in filtered.iterrows():
        st.markdown(f"""
        ### [{row['title']}]({row['url']})
        **Company:** {row['company']}  
        **Location:** {row['location']}  
        **Score:** {row['score']:.3f}  
        **Summary:** {row['summary']}
        """)

    st.page_link("pages/2_Select_Resume.py", label="🔁 Start Over")
