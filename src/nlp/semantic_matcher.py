from sentence_transformers import SentenceTransformer, util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# You can move this to config/settings.py later if you want to make it configurable
SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2' # A good balance of size and performance
# Other popular models: 'all-mpnet-base-v2', 'multi-qa-mpnet-base-dot-v1'

class SemanticMatcher:
    """
    Handles semantic similarity calculations between texts using Sentence Transformers.
    """
    def __init__(self):
        """
        Initializes the SemanticMatcher by loading the SentenceTransformer model.
        """
        try:
            self.model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
            logger.info(f"Sentence Transformer model '{SENTENCE_TRANSFORMER_MODEL}' loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading Sentence Transformer model '{SENTENCE_TRANSFORMER_MODEL}': {e}")
            logger.warning("Please ensure 'sentence-transformers' is installed: pip install sentence-transformers")
            raise # Re-raise to indicate a critical setup failure

    def get_embedding(self, text: str):
        """
        Generates a semantic embedding (vector) for the given text.

        Args:
            text (str): The input text.

        Returns:
            torch.Tensor: A tensor representing the semantic embedding of the text.
        """
        if not text:
            return None
        # Encode the text to get its embedding
        # convert_to_tensor=True ensures it returns a PyTorch tensor, which is what util.cos_sim expects
        embedding = self.model.encode(text, convert_to_tensor=True)
        return embedding

    def calculate_similarity(self, embedding1, embedding2) -> float:
        """
        Calculates the cosine similarity between two semantic embeddings.

        Args:
            embedding1 (torch.Tensor): The first text embedding.
            embedding2 (torch.Tensor): The second text embedding.

        Returns:
            float: The cosine similarity score (between -1 and 1).
        """
        if embedding1 is None or embedding2 is None:
            return 0.0 # Or handle as an error if embeddings are expected

        # Cosine similarity is a common metric for semantic similarity
        # util.cos_sim returns a tensor, so we convert it to a float
        cosine_similarity = util.cos_sim(embedding1, embedding2).item()
        return cosine_similarity

    def get_semantic_score(self, text1: str, text2: str) -> float:
        """
        Calculates the semantic similarity score between two raw text strings.

        Args:
            text1 (str): The first text (e.g., resume summary/skills).
            text2 (str): The second text (e.g., job description/requirements).

        Returns:
            float: The semantic similarity score (between -1 and 1).
        """
        if not text1 or not text2:
            logger.warning("One or both texts are empty for semantic similarity calculation. Returning 0.0.")
            return 0.0

        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)

        return self.calculate_similarity(embedding1, embedding2)

# --- For Testing / Example Usage ---
if __name__ == "__main__":
    print("--- Testing SemanticMatcher ---")

    try:
        matcher = SemanticMatcher()

        # Sample texts
        resume_summary = "Experienced Python developer with a strong background in machine learning and data analysis."
        job_description_ml = "We are seeking a talented Machine Learning Engineer to develop and deploy AI solutions."
        job_description_hr = "Looking for an HR Manager to handle employee relations and recruitment."
        empty_text = ""

        # Test 1: Highly similar texts
        score1 = matcher.get_semantic_score(resume_summary, job_description_ml)
        print(f"\nSimilarity (Resume Summary vs. ML Job): {score1:.4f}") # Expecting a high score

        # Test 2: Less similar texts
        score2 = matcher.get_semantic_score(resume_summary, job_description_hr)
        print(f"Similarity (Resume Summary vs. HR Job): {score2:.4f}") # Expecting a low score

        # Test 3: One empty text
        score3 = matcher.get_semantic_score(resume_summary, empty_text)
        print(f"Similarity (Resume Summary vs. Empty Text): {score3:.4f}") # Expecting 0.0

        # Test 4: Both empty texts
        score4 = matcher.get_semantic_score(empty_text, empty_text)
        print(f"Similarity (Empty Text vs. Empty Text): {score4:.4f}") # Expecting 0.0


    except Exception as e:
        logger.error(f"An error occurred during SemanticMatcher testing: {e}")

    print("\n--- SemanticMatcher Test Complete ---")