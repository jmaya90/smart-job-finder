import requests
import pandas as pd
from dotenv import load_dotenv
import os
from utils.semantic_matcher import score_jobs_semantically

# Load environment variables
load_dotenv()
api_key = os.getenv("RAPIDAPI_KEY")

def search_jobs(query="Mechanical Designer", location="Vancouver, BC", pages=2):
    api_url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    jobs = []

    for page in range(pages):
        params = {
            "query": f"{query} in {location}",
            "page": page + 1
        }
        response = requests.get(api_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            continue

        data = response.json().get("data", [])
        for job in data:
            jobs.append({
                "title": job.get("job_title", ""),
                "company": job.get("employer_name", ""),
                "location": f"{job.get('job_city', '')}, {job.get('job_country', '')}",
                "summary": job.get("job_description", "")[:300].replace("\n", " "),
                "url": job.get("job_apply_link", "")
            })

    return pd.DataFrame(jobs)


if __name__ == "__main__":
    # Load resume text
    with open("../resumes/mechanical_engineer.txt", "r", encoding="utf-8") as f:
        resume_text = f.read()

    # Step 1: Scrape jobs
    df = search_jobs("Mechanical Designer", "Vancouver, BC", pages=2)

    if df.empty:
        print("No jobs found.")
    else:
        # Step 2: Score them using semantic similarity
        df = score_jobs_semantically(df, resume_text)

        # Step 3: Save results
        df.to_csv("data/ranked_jobs.csv", index=False)
        print(df[["title", "company", "score"]].head(10))
