import streamlit as st

st.title("📄 Step 1: Upload or Select Resume")

uploaded = st.file_uploader("Upload your resume (.txt)", type="txt")

if uploaded:
    resume_text = uploaded.read().decode("utf-8")
    st.session_state.resume_text = resume_text
    st.text_area("Resume Preview", resume_text, height=300)
    if st.button("Continue to Job Search"):
        st.switch_page("pages/3_Search_Jobs.py")
else:
    st.info("Please upload a `.txt` file to continue.")
