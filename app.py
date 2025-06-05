import streamlit as st
import os
import pandas as pd
from datetime import datetime
import io # Import io for handling file bytes

# Import your custom modules
from config.settings import settings
from src.database.db_manager import DBManager
from src.api.jsearch_api import JSearchAPI
from src.nlp.resume_parser import ResumeParser 
from src.matching.job_matcher import JobMatcher

# --- Streamlit App Configuration (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="Job Matcher & Tracker",
    page_icon="🔍",
    layout="wide"
)

# --- Initialize Global Components (Cached for Performance) ---
# Use st.cache_resource to avoid re-initializing heavy NLP models on every rerun
# These functions will only run once per session due to caching.
@st.cache_resource
def get_db_manager():
    """Initializes and returns a cached DBManager instance."""
    return DBManager()

@st.cache_resource
def get_jsearch_api():
    """Initializes and returns a cached JSearchAPI instance."""
    return JSearchAPI()

@st.cache_resource
def get_job_matcher():
    """
    Initializes and returns a cached JobMatcher instance.
    JobMatcher internally initializes ResumeParser and SemanticMatcher.
    """
    return JobMatcher()

# Get instances of the cached components
db_manager = get_db_manager()
jsearch_api = get_jsearch_api()
job_matcher = get_job_matcher() # This instance contains resume_parser and semantic_matcher

# --- App Title and Introduction ---
st.title("🔍 Smart Job Finder & Tracker")
st.markdown("Find jobs relevant to your resume and keep track of your applications.")

# --- Session State Initialization ---
# Initialize session state variables to store data across Streamlit reruns
if 'parsed_resume' not in st.session_state:
    st.session_state.parsed_resume = None
if 'jobs_data' not in st.session_state:
    st.session_state.jobs_data = [] # Stores jobs from DB with match scores
if 'selected_resume_file_name' not in st.session_state:
    st.session_state.selected_resume_file_name = "None selected"

# --- Sidebar for Resume Management ---
st.sidebar.header("📝 Resume Management")

# Option 1: Upload a new resume file (PDF or TXT)
uploaded_file = st.sidebar.file_uploader(
    "Upload your resume (PDF or TXT):",
    type=["pdf", "txt"],
    key="resume_uploader" # Unique key for this widget
)

# Process uploaded file if a new one is provided
if uploaded_file is not None:
    # Check if a new file was uploaded or if it's the same file from a previous rerun
    # (Streamlit re-runs the script on every interaction, so check for changes)
    if st.session_state.selected_resume_file_name != uploaded_file.name:
        st.session_state.selected_resume_file_name = uploaded_file.name
        with st.spinner(f"Parsing uploaded file: {uploaded_file.name}..."):
            # Call parse_resume on the job_matcher's resume_parser instance
            st.session_state.parsed_resume = job_matcher.resume_parser.parse_resume(uploaded_file, is_file_path=False)
            if st.session_state.parsed_resume and st.session_state.parsed_resume['text']:
                st.sidebar.success(f"'{uploaded_file.name}' loaded and parsed.")
            else:
                st.sidebar.error(f"Failed to parse '{uploaded_file.name}'. Please check the file content.")
                st.session_state.parsed_resume = None

# Option 2: Select an existing resume file from the 'resumes' directory
# This option is shown if no file is currently uploaded, or if the user wants to switch back
# The 'uploaded_file is None' ensures that the file_uploader takes precedence
if uploaded_file is None:
    # List all .txt and .pdf files in the resumes directory
    resume_files = [f for f in os.listdir(settings.RESUME_DIR) if f.lower().endswith(('.txt', '.pdf'))]
    resume_files.insert(0, "Select an existing resume...") # Add a default option

    selected_existing_resume = st.sidebar.selectbox(
        "Or choose from existing resumes:",
        options=resume_files,
        key="existing_resume_selector" # Unique key for this widget
    )

    # Process selected existing file
    if selected_existing_resume != "Select an existing resume..." and st.session_state.selected_resume_file_name != selected_existing_resume:
        st.session_state.selected_resume_file_name = selected_existing_resume
        resume_path = os.path.join(settings.RESUME_DIR, selected_existing_resume)
        with st.spinner(f"Parsing existing file: {selected_existing_resume}..."):
            # Call parse_resume on the job_matcher's resume_parser instance
            st.session_state.parsed_resume = job_matcher.resume_parser.parse_resume(resume_path, is_file_path=True)
            if st.session_state.parsed_resume and st.session_state.parsed_resume['text']:
                st.sidebar.success(f"'{selected_existing_resume}' loaded and parsed.")
            else:
                st.sidebar.error(f"Failed to parse '{selected_existing_resume}'. Please check the file content.")
                st.session_state.parsed_resume = None

# Display current resume status in the sidebar
st.sidebar.write("---")
st.sidebar.subheader("Currently Loaded Resume:")
if st.session_state.parsed_resume:
    st.sidebar.write(f"**File:** {st.session_state.selected_resume_file_name}")
    st.sidebar.write(f"**Skills found:** {len(st.session_state.parsed_resume['skills'])}")
    st.sidebar.write(f"**Keywords found:** {len(st.session_state.parsed_resume['keywords'])}")
    st.sidebar.info("You can now fetch and match jobs!")
else:
    st.sidebar.info("Please upload or select a resume to get started.")

# --- Job Search Section ---
st.header("Job Search Criteria")
col1, col2, col3 = st.columns(3)

with col1:
    search_query = st.text_input("Job Title / Keywords", value="Python Developer", key="search_query")
with col2:
    search_location = st.text_input("Location (City, State, Country)", value="New York", key="search_location")
with col3:
    num_pages_to_fetch = st.number_input("Number of pages to fetch", min_value=1, max_value=5, value=1, step=1, key="num_pages")

st.subheader("Advanced Filters (Optional)")
col_adv1, col_adv2, col_adv3 = st.columns(3)
with col_adv1:
    date_posted_options = ["all", "today", "3days", "week", "month"]
    selected_date_posted = st.selectbox("Date Posted", options=date_posted_options, key="date_posted")
with col_adv2:
    employment_type_options = ["", "fulltime", "parttime", "contract", "internship"]
    selected_employment_type = st.selectbox("Employment Type", options=employment_type_options, key="employment_type")
with col_adv3:
    remote_only = st.checkbox("Remote Jobs Only", key="remote_only")

# Button to trigger fetching and matching
if st.button("Fetch & Match Jobs", type="primary"):
    if not st.session_state.parsed_resume:
        st.error("Please load a resume first before fetching jobs.")
    else:
        with st.spinner("Fetching jobs and calculating matches... This might take a moment."):
            # Fetch jobs from JSearch API
            fetched_jobs_raw = jsearch_api.search_jobs(
                query=search_query,
                location=search_location,
                num_pages=num_pages_to_fetch,
                date_posted=selected_date_posted if selected_date_posted != "all" else None,
                remote_jobs_only=remote_only,
                employment_type=selected_employment_type if selected_employment_type else None
            )

            new_jobs_count = 0
            # Process and store newly fetched jobs into the database
            for job in fetched_jobs_raw:
                # db_manager.insert_job returns True if new, False if duplicate or error
                if db_manager.insert_job(job): 
                    new_jobs_count += 1
            
            st.success(f"Fetched {len(fetched_jobs_raw)} jobs. {new_jobs_count} new jobs added to database.")
            st.toast(f"{new_jobs_count} new jobs added!")

            # Retrieve ALL jobs from DB for matching (including previously fetched ones)
            all_jobs_from_db = db_manager.get_all_jobs()
            
            # Calculate scores for all jobs against the currently loaded resume
            jobs_with_scores = []
            if all_jobs_from_db:
                for job in all_jobs_from_db:
                    match_result = job_matcher.match_job_to_resume(st.session_state.parsed_resume, job)
                    # Merge job data with match scores for display
                    job_with_score = {**job, **match_result} 
                    jobs_with_scores.append(job_with_score)
                
                # Sort jobs by final_score in descending order (highest relevance first)
                st.session_state.jobs_data = sorted(jobs_with_scores, key=lambda x: x['final_score'], reverse=True)
                st.toast("Matching complete!")
            else:
                st.session_state.jobs_data = []
                st.warning("No jobs found in the database to match.")

# --- Display Matched Job Listings ---
st.header("Matched Job Listings")

if not st.session_state.jobs_data:
    st.info("No jobs to display yet. Please load a resume and fetch jobs.")
else:
    st.write(f"Displaying {len(st.session_state.jobs_data)} matched jobs, sorted by relevance.")

    # Status filter for displayed jobs
    st.subheader("Filter by Status")
    status_options = ["All", "new", "seen", "applied", "interviewing", "rejected"]
    selected_status_filter = st.multiselect("Select statuses to display:", options=status_options, default=["All"])

    filtered_jobs = []
    if "All" in selected_status_filter:
        filtered_jobs = st.session_state.jobs_data
    else:
        # Filter jobs whose status is in the selected_status_filter list
        filtered_jobs = [job for job in st.session_state.jobs_data if job['status'] in selected_status_filter]

    if not filtered_jobs:
        st.info("No jobs found matching the selected status filters.")
    else:
        # Iterate through filtered jobs and display them
        for job in filtered_jobs:
            job_id_db = job['job_id'] # Use JSearch's unique job_id for keying

            # Use an expander for each job to show/hide details
            with st.expander(f"**{job['job_title']}** at **{job['company_name']}** (Score: {job['final_score']}%) - Status: **{job['status'].upper()}**"):
                st.markdown(f"**Location:** {job['location']}")
                st.markdown(f"**Employment Type:** {job['job_employment_type']}")
                st.markdown(f"**Posted (UTC):** {job['job_posted_at_datetime_utc']}")
                if job['job_url']:
                    st.markdown(f"**Apply Link:** [Click Here]({job['job_url']})")
                if job['employer_website']:
                    st.markdown(f"**Company Website:** [Click Here]({job['employer_website']})")

                st.subheader("Match Details")
                st.write(f"**Keyword Match:** {job['keyword_score']}%")
                st.write(f"**Semantic Match:** {job['semantic_score']}%")
                if job.get('matched_keywords'): # Display matched keywords if available
                    st.write(f"**Common Keywords:** {', '.join(job['matched_keywords'])}")

                st.subheader("Job Description")
                st.write(job['job_description'])

                # Status update functionality for individual jobs
                current_status = job['status']
                new_status = st.selectbox(
                    f"Update Status for {job_id_db}:", # Label for the selectbox
                    options=status_options[1:], # Options are "new", "seen", "applied", etc. (excluding "All")
                    # Set default selected option to the job's current status
                    index=status_options[1:].index(current_status) if current_status in status_options[1:] else 0,
                    key=f"status_select_{job_id_db}" # Unique key for each selectbox per job
                )

                if st.button(f"Save Status for {job_id_db}", key=f"save_status_{job_id_db}"):
                    if db_manager.update_job_status(job_id_db, new_status):
                        st.success(f"Status for '{job['job_title']}' updated to '{new_status}'.")
                        # To refresh the display with the new status, clear cached job data
                        # and force a rerun of the Streamlit script. This is simple but re-computes all.
                        st.session_state.jobs_data = [] 
                        st.rerun()
                    else:
                        st.error(f"Failed to update status for '{job['job_title']}'.")