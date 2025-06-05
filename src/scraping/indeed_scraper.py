import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_indeed(query, location, pages=1):
    jobs = []
    base_url = "https://ca.indeed.com/jobs"

    for page in range(pages):
        params = {
            "q": query,
            "l": location,
            "start": page * 10
        }
        response = requests.get(base_url, params=params)
        soup = BeautifulSoup(response.text, "html.parser")
        
        for card in soup.find_all("a", class_="tapItem"):
            job_title = card.find("h2").text.strip()
            company = card.find("span", class_="companyName").text.strip()
            location = card.find("div", class_="companyLocation").text.strip()
            summary = card.find("div", class_="job-snippet").text.strip().replace("\n", " ")
            link = "https://ca.indeed.com" + card.get("href")
            jobs.append({
                "title": job_title,
                "company": company,
                "location": location,
                "summary": summary,
                "url": link
            })

    return pd.DataFrame(jobs)

# Example usage
if __name__ == "__main__":
    df = scrape_indeed("Mechanical Designer", "Vancouver, BC", pages=2)
    df.to_csv("data/scraped_jobs.csv", index=False)
    print(df.head())
