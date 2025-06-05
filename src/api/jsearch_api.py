import requests
import logging
import time # For potential rate limiting or delays
from config.settings import settings # Import your settings

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSearchAPI:
    """
    Manages API requests to the JSearch API via RapidAPI.
    """
    BASE_URL = "https://jsearch.p.rapidapi.com/"
    # Common endpoints, add more as needed:
    ENDPOINTS = {
        "search": "search",
        "job_details": "job-details",
        "search_filters": "search-filters", # Useful for understanding available filters
    }

    def __init__(self):
        """
        Initializes the JSearchAPI client with necessary headers.
        """
        self.headers = {
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            "X-RapidAPI-Key": settings.JSEARCH_API_KEY # Get API key from your settings
        }
        if not settings.JSEARCH_API_KEY:
            logger.error("JSEARCH_API_KEY not found in environment variables. Please set it in your .env file.")
            raise ValueError("JSEARCH_API_KEY is missing. Cannot proceed without API access.")

    def _make_request(self, endpoint: str, params: dict) -> dict | None:
        """
        Internal helper method to make a request to the JSearch API.

        Args:
            endpoint (str): The specific API endpoint (e.g., "search").
            params (dict): Dictionary of query parameters for the request.

        Returns:
            dict | None: The JSON response data, or None if an error occurred.
        """
        url = f"{self.BASE_URL}{self.ENDPOINTS[endpoint]}"
        max_retries = 3
        retry_delay = 5 # seconds

        for attempt in range(max_retries):
            try:
                logger.info(f"Making API request to {endpoint} (Attempt {attempt + 1}/{max_retries}) with params: {params}")
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                return response.json()
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error for {endpoint} (Status {e.response.status_code}): {e}")
                if e.response.status_code == 429: # Rate limit exceeded
                    logger.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2 # Exponential backoff
                elif 400 <= e.response.status_code < 500:
                    logger.error(f"Client error. Check request parameters. Response: {e.response.text}")
                    return None # Don't retry client errors unless explicitly handled
                else: # Server errors
                    logger.warning(f"Server error. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection Error for {endpoint}: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            except requests.exceptions.Timeout as e:
                logger.error(f"Timeout Error for {endpoint}: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
            except Exception as e:
                logger.error(f"An unexpected error occurred for {endpoint}: {e}")
                return None # For unexpected errors, don't retry

        logger.error(f"Failed to fetch data from {endpoint} after {max_retries} attempts.")
        return None

    def search_jobs(self, query: str, location: str = None, page: int = 1, num_pages: int = 1,
                    date_posted: str = None, remote_jobs_only: bool = False,
                    employment_type: str = None, experience_level: str = None) -> list[dict]:
        """
        Searches for job listings based on provided criteria.

        Args:
            query (str): The job query (e.g., "Python developer").
            location (str, optional): City, state, or country. Defaults to None.
            page (int, optional): The page number of results to retrieve. Defaults to 1.
            num_pages (int, optional): The total number of pages to fetch. Defaults to 1.
                                       Use caution with high values to avoid rate limits.
            date_posted (str, optional): Filters jobs by date posted (e.g., "today", "3days", "week", "month").
            remote_jobs_only (bool, optional): If True, filters for remote jobs.
            employment_type (str, optional): Filter by employment type (e.g., "fulltime", "contract").
            experience_level (str, optional): Filter by experience (e.g., "entry_level", "mid_level", "senior_level").


        Returns:
            list[dict]: A list of job dictionaries. Each dictionary contains job details
                        as returned by the JSearch API. Returns an empty list on failure.
        """
        all_jobs = []
        for p in range(page, page + num_pages):
            params = {
                "query": query,
                "page": str(p),
            }
            if location:
                params["query"] += f" in {location}" # JSearch often prefers location in query for simplicity
                # Alternatively, use job_location param if available and separate
                # params["job_location"] = location # Check JSearch docs for precise param
            if date_posted:
                params["date_posted"] = date_posted
            if remote_jobs_only:
                params["remote_jobs_only"] = "true" # JSearch expects "true" as string
            if employment_type:
                params["employment_type"] = employment_type
            if experience_level:
                params["job_requirements"] = experience_level # JSearch can use this for exp level

            response_data = self._make_request("search", params)
            if response_data and response_data.get("data"):
                # Add source information to each job
                for job in response_data["data"]:
                    job['api_source'] = 'jsearch'
                all_jobs.extend(response_data["data"])
            else:
                logger.warning(f"No data returned for query '{query}', page {p} or API error.")
                # If a page fails, subsequent pages might also fail due to rate limits or invalid query
                if response_data is None: # Only break if a critical error or rate limit
                    break
            time.sleep(0.5) # Small delay between page requests to be polite to API
        return all_jobs

    def get_job_details(self, job_id: str) -> dict | None:
        """
        Retrieves detailed information for a specific job.

        Args:
            job_id (str): The unique ID of the job.

        Returns:
            dict | None: A dictionary containing detailed job information, or None on failure.
        """
        params = {"job_id": job_id}
        response_data = self._make_request("job_details", params)
        if response_data and response_data.get("data"):
            return response_data["data"][0] if response_data["data"] else None
        return None


# --- For Testing / Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: Ensure your .env file is in the project root with JSEARCH_API_KEY
    # and config/settings.py is set up correctly.

    print("--- Testing JSearchAPI ---")
    try:
        jsearch_api = JSearchAPI()

        print("\nSearching for 'Python developer' jobs in 'New York', 2 pages, posted last week...")
        jobs = jsearch_api.search_jobs(
            query="Python developer",
            location="New York",
            num_pages=2,
            date_posted="week",
            employment_type="fulltime"
        )
        print(f"Found {len(jobs)} jobs.")

        if jobs:
            print("\nFirst job found:")
            first_job = jobs[0]
            print(f"  Title: {first_job.get('job_title')}")
            print(f"  Company: {first_job.get('employer_name')}")
            print(f"  Location: {first_job.get('job_city')}, {first_job.get('job_state')}")
            print(f"  URL: {first_job.get('job_apply_link')}")
            print(f"  Job ID: {first_job.get('job_id')}")

            # Test fetching details for the first job
            if first_job.get('job_id'):
                print(f"\nFetching details for Job ID: {first_job['job_id']}")
                job_details = jsearch_api.get_job_details(first_job['job_id'])
                if job_details:
                    print(f"  Detailed description length: {len(job_details.get('job_description', ''))} characters")
                    print(f"  Qualifications: {job_details.get('job_highlights', {}).get('qualifications')}")
                else:
                    print("  Could not retrieve job details.")
        else:
            print("No jobs found for the specified query.")

    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unhandled error occurred during API testing: {e}")

    print("\n--- JSearchAPI Test Complete ---")