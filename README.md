# 🚀 Smart Job Finder & Tracker

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 About The Project

The **Smart Job Finder & Tracker** is an intelligent application designed to revolutionize the job search process. Moving beyond traditional keyword-only matching, this tool leverages advanced Natural Language Processing (NLP) and Large Language Models (LLMs) to understand the semantic meaning behind both a job seeker's resume and detailed job descriptions. Its goal is to identify highly relevant job opportunities and provide a robust system for tracking application progress, making job hunting more efficient and insightful.

**Key problems this project aims to solve:**
* The inefficiency and tedium of manual job searching.
* Missing out on suitable opportunities due to superficial keyword matches.
* Lack of a centralized, smart system for managing job applications.

## ✨ Features

* **Intelligent Job Matching:** Calculates a nuanced "relevance score" for each job by combining:
    * **Keyword Overlap:** Direct matching of skills and terms.
    * **Semantic Similarity:** Deep understanding of meaning using LLM-powered embeddings.
* **Resume Parsing:** Automatically extracts key skills and general keywords from resume text.
* **Dynamic Job Fetching:** Integrates with the JSearch API to fetch up-to-date job listings based on customizable search criteria (title, location, type, etc.).
* **Local Database Storage:** Stores fetched job data in a local SQLite database, efficiently handling new entries and preventing duplicates.
* **Interactive Web Interface:** A user-friendly application built with Streamlit for seamless interaction.
* **Application Tracking:** Allows users to easily update and manage job statuses (e.g., `new`, `seen`, `applied`, `interviewing`, `rejected`).
* **Status Filtering:** Filter and view jobs based on their current application status.

## 🛠️ Technology Stack

* **Language:** Python 3.9+
* **Web Framework:** [Streamlit](https://streamlit.io/)
* **Database:** SQLite3
* **Job API:** JSearch API (via RapidAPI)
* **Natural Language Processing (NLP):**
    * [spaCy](https://spacy.io/) (`en_core_web_sm` for keyword extraction)
    * [Sentence Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2` for semantic embeddings)
* **Environment Management:** `venv`
* **Configuration:** `python-dotenv`

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

* Python 3.9 or higher installed.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [Your_GitHub_Repository_URL]
    cd job_scraper
    ```
2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```
3.  **Install project dependencies:**
    First, ensure you have a `requirements.txt` file. If not, generate one by running `pip freeze > requirements.txt` (after you've installed all libraries like `streamlit`, `requests`, `spacy`, `sentence-transformers`, `python-dotenv`, `pandas`).
    Then, install them:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Download the spaCy NLP model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

### API Key Setup

1.  **Obtain a JSearch API Key:**
    * Visit the [RapidAPI JSearch API page](https://rapidapi.com/apidojo/api/jsearch/).
    * Sign up/Log in and subscribe to the free (Basic) tier.
    * Locate your API Key (typically found under `X-RapidAPI-Key` in the endpoint examples).
2.  **Create a `.env` file:**
    * In the root directory of your project (`job_scraper/`), create a new file named `.env`.
    * Add your JSearch API key to this file:
        ```
        JSEARCH_API_KEY="YOUR_RAPIDAPI_JSEARCH_API_KEY_HERE"
        ```
    * **Important:** Ensure `.env` is listed in your `.gitignore` file to prevent accidentally committing your API key to GitHub.

## 🏃 Usage

1.  **Activate your virtual environment.**
2.  **Run the Streamlit application from the project root directory:**
    ```bash
    streamlit run app.py
    ```
3.  Your default web browser should automatically open to the app (usually `http://localhost:8501`).
4.  **Within the Application:**
    * Use the sidebar to **select a resume** from the `resumes/` folder (or add your own `.txt` file).
    * Enter your desired **job search criteria** (job title, location, filters).
    * Click the **"Fetch & Match Jobs"** button. The app will fetch new jobs and calculate their relevance scores.
    * Explore the **matched job listings**, which are sorted by relevance. Expand each job to see details and use the dropdown to **update its application status**.

## 📁 Project Structure
job_scraper/
├── .venv/                         # Python Virtual Environment (ignored by Git)
├── config/                        # Application configuration files
│   └── settings.py                # Core settings, API key loading
├── data/                          # Stores local data
│   └── job_database.db            # SQLite database
├── src/                           # Source code for core functionalities
│   ├── api/
│   │   └── jsearch_api.py         # JSearch API client
│   ├── database/
│   │   └── db_manager.py          # Database operations
│   ├── matching/
│   │   └── job_matcher.py         # Orchestrates job matching logic
│   └── nlp/
│       ├── resume_parser.py       # Handles resume text processing
│       └── semantic_matcher.py    # Manages LLM embeddings and similarity
├── resumes/                       # Example and user-provided resumes (.txt)
├── .env                           # Environment variables (private, ignored by Git)
├── .gitignore                     # Git ignore file
├── app.py                         # Main Streamlit application entry point
├── README.md                      # This file
└── requirements.txt               # List of Python dependencies

## 🗺️ Roadmap & Future Enhancements

This project is under active development, and exciting enhancements are planned:

* **Advanced LLM Integrations:**
    * **Intelligent Resume Tailoring:** Provide context-aware suggestions for optimizing resumes based on specific job descriptions.
    * **Automated Cover Letter Drafting:** Generate personalized cover letter drafts using LLMs.
    * **Interview Preparation Assistant:** Offer insights into common interview questions and topics based on job requirements.
* **Proactive Skill Gap Analysis:** Suggest skills to acquire based on desired career paths and job market trends.
* **Enhanced User Experience:** Continuous improvements to the Streamlit UI/UX.
* **Refined Matching Logic:** Further optimization of relevance scoring algorithms.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please feel free to:
1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## ✉️ Contact

* **Name:** Juan Sebastian Maya
* **Email:** jsebasmm@gmail.com
* **LinkedIn:** [linkedin.com/in/juan-s-maya-m](https://www.linkedin.com/in/juan-s-maya-m)
* **GitHub Profile:** [github.com/jmaya90](https://github.com/jmaya90)

Project Link: [https://github.com/jmaya90/smart-job-finder](https://github.com/jmaya90/smart-job-finder)

---