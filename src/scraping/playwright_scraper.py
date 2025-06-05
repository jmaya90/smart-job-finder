import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def scrape_indeed(query, location, pages=1):
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for page_num in range(pages):
            start = page_num * 10
            url = f"https://ca.indeed.com/jobs?q={query}&l={location}&start={start}"
            await page.goto(url)
            #print(await page.content())

            job_cards = await page.query_selector_all("a.tapItem")

            for card in job_cards:
                title = await card.query_selector_eval("h2", "el => el.innerText") or ""
                company = await card.query_selector_eval(".companyName", "el => el.innerText") or ""
                loc = await card.query_selector_eval(".companyLocation", "el => el.innerText") or ""
                summary = await card.query_selector_eval(".job-snippet", "el => el.innerText") or ""
                link = await card.get_attribute("href")

                jobs.append({
                    "title": title.strip(),
                    "company": company.strip(),
                    "location": loc.strip(),
                    "summary": summary.strip().replace("\n", " "),
                    "url": "https://ca.indeed.com" + link if link else ""
                })

        await browser.close()

    return pd.DataFrame(jobs)

if __name__ == "__main__":
    df = asyncio.run(scrape_indeed("Mechanical+Designer", "Vancouver", pages=2))
    df.to_csv("data/scraped_jobs.csv", index=False)
    print(df.head())
