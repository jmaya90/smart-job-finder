import logging
import os
from collections import Counter
from config.settings import settings
from src.nlp.resume_parser import ResumeParser # Only import the class
from src.nlp.semantic_matcher import SemanticMatcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobMatcher:
    """
    Combines keyword-based and semantic-based matching to calculate job relevance.
    """
    def __init__(self):
        """
        Initializes the JobMatcher by creating instances of ResumeParser and SemanticMatcher.
        """
        self.resume_parser = ResumeParser() # Will load spaCy model
        self.semantic_matcher = SemanticMatcher() # Will load sentence-transformer model
        logger.info("JobMatcher initialized with ResumeParser and SemanticMatcher.")

    def _calculate_keyword_overlap_score(self, resume_keywords: list[str], job_keywords: list[str]) -> float:
        """
        Calculates a keyword overlap score between resume and job.
        Uses Jaccard similarity for now, can be improved.
        """
        if not resume_keywords or not job_keywords:
            return 0.0

        resume_set = set(resume_keywords)
        job_set = set(job_keywords)

        intersection = len(resume_set.intersection(job_set))
        union = len(resume_set.union(job_set))

        if union == 0:
            return 0.0

        score = intersection / union
        return score

    def match_job_to_resume(self, resume_parsed_data: dict, job_data: dict) -> dict:
        """
        Calculates a comprehensive match score between a resume and a job posting.

        Args:
            resume_parsed_data (dict): Dictionary containing parsed resume info
                                       (e.g., {'text': ..., 'skills': [...], 'keywords': [...]}).
            job_data (dict): Dictionary containing job posting details.
                             Expected keys: 'job_description', 'job_title'.

        Returns:
            dict: A dictionary containing the final score and individual scores.
        """
        resume_text = resume_parsed_data.get('text', '')
        resume_skills = resume_parsed_data.get('skills', [])
        resume_keywords = resume_parsed_data.get('keywords', [])

        job_description = job_data.get('job_description', '')
        job_title = job_data.get('job_title', '')

        if not resume_text or not job_description:
            logger.warning("Resume text or job description is empty. Cannot calculate match score.")
            return {"final_score": 0.0, "keyword_score": 0.0, "semantic_score": 0.0}

        # 1. Keyword Overlap Score
        # Extract keywords/skills from job description using the resume parser's logic
        # You might want a dedicated 'JobDescriptionParser' if job data structure varies
        job_description_skills = self.resume_parser.extract_skills(job_description + " " + job_title)
        job_description_keywords = self.resume_parser.extract_general_keywords(job_description)

        # Use resume's extracted skills/keywords vs. job's extracted skills/keywords
        # You can prioritize skills over general keywords. For simplicity, let's use all keywords for now.
        keyword_score = self._calculate_keyword_overlap_score(resume_keywords, job_description_keywords)
        logger.info(f"Keyword score: {keyword_score:.4f}")

        # 2. Semantic Similarity Score
        # We can calculate semantic similarity between the full resume text and the full job description.
        # Or you could combine specific sections, e.g., resume skills + experience vs. job description + requirements.
        semantic_score = self.semantic_matcher.get_semantic_score(resume_text, job_description)
        logger.info(f"Semantic score: {semantic_score:.4f}")

        # 3. Combine Scores with Weights
        # Ensure weights are defined in config/settings.py
        # You can adjust these weights based on your preferences and testing.
        # Ensure semantic_score is normalized to 0-1 if not already (cosine similarity is -1 to 1, but usually 0 to 1 for relevant texts)
        # We can map it: (score + 1) / 2 to map -1 to 1 to 0 to 1
        normalized_semantic_score = (semantic_score + 1) / 2 # Normalize from [-1, 1] to [0, 1]

        # Use weights from settings
        final_score = (keyword_score * settings.KEYWORD_WEIGHT) + \
                      (normalized_semantic_score * settings.SEMANTIC_WEIGHT)

        # Optional: Apply thresholding if semantic score is too low, the keyword score might not matter much
        # if normalized_semantic_score < settings.SEMANTIC_THRESHOLD:
        #     final_score *= 0.5 # Penalize if semantic match is very weak

        final_score = round(final_score * 100, 2) # Convert to percentage, round to 2 decimal places

        return {
            "final_score": final_score,
            "keyword_score": round(keyword_score * 100, 2),
            "semantic_score": round(normalized_semantic_score * 100, 2),
            "matched_keywords": list(set(resume_keywords).intersection(set(job_description_keywords))) # For display
        }


# --- For Testing / Example Usage ---
if __name__ == "__main__":
    print("--- Testing JobMatcher ---")

    # Ensure your resume file exists
    RESUME_PATH = os.path.join(settings.RESUME_DIR, "mechanical_engineer.txt") # Use settings for path if available
    if not os.path.exists(RESUME_PATH):
        # Fallback if settings.RESUME_DIR is not set or file not found
        RESUME_PATH = os.path.join("resumes", "mechanical_engineer.txt")
        if not os.path.exists(RESUME_PATH):
            print(f"Error: Resume file not found at {RESUME_PATH}. Please create it or adjust the path.")
            exit()

    try:
        # 1. Parse the resume once
        temp_parser = ResumeParser() # Using a temp parser for the test setup
        parsed_resume = temp_parser.parse_resume(RESUME_PATH)
        print(f"\nLoaded resume from: {parsed_resume['file_path']}")
        print(f"Resume skills: {parsed_resume['skills'][:5]}...") # Show first few for brevity
        print(f"Resume keywords: {parsed_resume['keywords'][:5]}...") # Show first few for brevity
        del temp_parser # Clean up temp parser

        matcher = JobMatcher()

        # Sample Job Data 1: Highly relevant (Python, ML, Data)
        job_data_1 = {
            "job_title": "Senior Machine Learning Engineer",
            "job_description": "We are seeking a highly skilled Python developer with expertise in machine learning, deep learning, and data analysis. Experience with AWS and SQL databases is a plus. Build and deploy scalable AI solutions."
        }

        # Sample Job Data 2: Somewhat relevant (Python, but different focus)
        job_data_2 = {
            "job_title": "Backend Python Developer",
            "job_description": "Develop robust backend services using Python and Flask. Experience with REST APIs and PostgreSQL required. Familiarity with agile methodologies is a plus."
        }

        # Sample Job Data 3: Not relevant
        job_data_3 = {
            "job_title": "Human Resources Manager",
            "job_description": "Manage HR operations, including recruitment, employee relations, and compensation. Strong communication skills required."
        }

        # Sample Job Data 4: Empty description
        job_data_4 = {
            "job_title": "Empty Job",
            "job_description": ""
        }

        print("\n--- Matching Resume to Sample Job 1 (Highly Relevant) ---")
        match_result_1 = matcher.match_job_to_resume(parsed_resume, job_data_1)
        print(f"Final Score: {match_result_1['final_score']}%")
        print(f"Keyword Score: {match_result_1['keyword_score']}%")
        print(f"Semantic Score: {match_result_1['semantic_score']}%")
        print(f"Matched Keywords: {match_result_1['matched_keywords'][:5]}...") # Show first few

        print("\n--- Matching Resume to Sample Job 2 (Somewhat Relevant) ---")
        match_result_2 = matcher.match_job_to_resume(parsed_resume, job_data_2)
        print(f"Final Score: {match_result_2['final_score']}%")
        print(f"Keyword Score: {match_result_2['keyword_score']}%")
        print(f"Semantic Score: {match_result_2['semantic_score']}%")
        print(f"Matched Keywords: {match_result_2['matched_keywords'][:5]}...")

        print("\n--- Matching Resume to Sample Job 3 (Not Relevant) ---")
        match_result_3 = matcher.match_job_to_resume(parsed_resume, job_data_3)
        print(f"Final Score: {match_result_3['final_score']}%")
        print(f"Keyword Score: {match_result_3['keyword_score']}%")
        print(f"Semantic Score: {match_result_3['semantic_score']}%")

        print("\n--- Matching Resume to Sample Job 4 (Empty Description) ---")
        match_result_4 = matcher.match_job_to_resume(parsed_resume, job_data_4)
        print(f"Final Score: {match_result_4['final_score']}%")

    except Exception as e:
        logger.error(f"An error occurred during JobMatcher testing: {e}")

    print("\n--- JobMatcher Test Complete ---")