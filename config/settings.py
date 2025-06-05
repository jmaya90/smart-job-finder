import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    JSEARCH_API_KEY: str = os.getenv("JSEARCH_API_KEY") # No default needed if it *must* come from .env
    # Add other settings here, ensure proper type hints
    DB_PATH: str = "data/job_database.db"
    SEMANTIC_THRESHOLD: float = 0.75 # Adjust as you fine-tune
    KEYWORD_WEIGHT: float = 0.5    # Adjust as you fine-tune
    SEMANTIC_WEIGHT: float = 0.5   # Sum of weights should usually be 1.0, or used relative to each other
    RESUME_DIR: str = "resumes/" # Directory where resumes are stored

settings = Settings()