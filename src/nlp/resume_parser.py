import spacy
import os
import re
import logging
from collections import Counter
import pypdf # Import the pypdf library

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load('en_core_web_sm')
            logger.info("SpaCy model 'en_core_web_sm' loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading SpaCy model: {e}. Please ensure it's installed (`python -m spacy download en_core_web_sm`).")
            self.nlp = None # Set to None if loading fails

        # Define common skills and keywords for a mechanical engineer (extend as needed)
        # These are examples, you'd want a more comprehensive list
        self.common_skills = [
            'CAD', 'SolidWorks', 'AutoCAD', 'Inventor', 'Fusion 360', 'CATIA',
            'ANSYS', 'FEA', 'CFD', 'Fluent', 'MATLAB', 'Simulink', 'Python', 'R',
            'C++', 'GD&T', 'DFM', 'Lean Manufacturing', 'Six Sigma', 'Prototyping',
            '3D Printing', 'CNC Machining', 'Robotics', 'Thermodynamics', 'Fluid Mechanics',
            'Heat Transfer', 'Materials Science', 'Finite Element Analysis', 'Design',
            'Stress Analysis', 'Kinematics', 'Dynamics', 'Mechatronics', 'Control Systems',
            'Jigs & Fixtures', 'Manufacturing', 'Assembly', 'Solid Modeling', 'Mechanical Design',
            'Tolerance Analysis', 'Failure Analysis', 'Root Cause Analysis', 'FMEA', 'P&ID'
        ]
        self.common_keywords = [
            'design', 'analysis', 'development', 'engineering', 'systems', 'project',
            'research', 'testing', 'prototyping', 'manufacturing', 'process', 'solution',
            'optimize', 'innovate', 'implement', 'manage', 'lead', 'collaborate', 'technical',
            'mechanical', 'product', 'problem-solving', 'troubleshooting', 'efficiency',
            'performance', 'quality', 'simulation', 'validation', 'documentation',
            'report', 'technical reports', 'client', 'vendor', 'supply chain'
        ]
        # Convert to lowercase for case-insensitive matching
        self.common_skills_lower = [s.lower() for s in self.common_skills]
        self.common_keywords_lower = [k.lower() for k in self.common_keywords]


    def _read_txt_text(self, file_path: str) -> str:
        """Reads text from a .txt file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"Successfully loaded resume text from {file_path}")
            return text
        except Exception as e:
            logger.error(f"Error reading .txt file {file_path}: {e}")
            return ""

    def _read_pdf_text(self, file_bytes) -> str:
        """Reads text from PDF file bytes."""
        text = ""
        try:
            reader = pypdf.PdfReader(file_bytes)
            for page in reader.pages:
                text += page.extract_text() or "" # extract_text can return None
            logger.info("Successfully extracted text from PDF file.")
            return text
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")
            return ""

    def parse_resume(self, resume_source, is_file_path: bool = True) -> dict:
        """
        Parses a resume from a file path (txt) or file bytes (pdf/txt upload).

        Args:
            resume_source: Either a file path (str) or file-like object (bytesIO)
            is_file_path: True if resume_source is a file path, False if it's file bytes
        """
        resume_text = ""
        if is_file_path:
            if not os.path.exists(resume_source):
                logger.error(f"Resume file not found at: {resume_source}")
                return {"text": "", "skills": [], "keywords": []}
            if resume_source.lower().endswith('.txt'):
                resume_text = self._read_txt_text(resume_source)
            else:
                logger.error(f"Unsupported file type for path: {resume_source}. Only .txt is supported via path.")
                return {"text": "", "skills": [], "keywords": []}
        else: # resume_source is file bytes (from st.file_uploader)
            if hasattr(resume_source, 'name') and resume_source.name.lower().endswith('.pdf'):
                resume_text = self._read_pdf_text(resume_source)
            elif hasattr(resume_source, 'name') and resume_source.name.lower().endswith('.txt'):
                 resume_text = resume_source.getvalue().decode('utf-8') # Read bytes and decode
                 logger.info("Successfully loaded resume text from uploaded .txt file.")
            else:
                logger.error("Unsupported uploaded file type. Only .pdf and .txt are supported.")
                return {"text": "", "skills": [], "keywords": []}

        if not resume_text:
            return {"text": "", "skills": [], "keywords": []}

        skills = self.extract_skills(resume_text)
        general_keywords = self.extract_general_keywords(resume_text)

        logger.info(f"Extracted {len(skills)} skills.")
        logger.info(f"Extracted {len(general_keywords)} general keywords.")

        return {"text": resume_text, "skills": skills, "keywords": general_keywords}

    def extract_skills(self, text: str) -> list[str]:
        """Extracts predefined skills from the resume text."""
        found_skills = []
        text_lower = text.lower()

        # Check for exact matches of predefined skills
        for skill in self.common_skills_lower:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.append(skill)

        # Further extraction using SpaCy's entity recognition or noun chunks could be added here
        # For a lighter approach, we stick to predefined lists for now.

        return sorted(list(set(found_skills))) # Remove duplicates and sort

    def extract_general_keywords(self, text: str) -> list[str]:
        """
        Extracts general keywords from the resume text using SpaCy's tokenization
        and matches against a predefined list.
        """
        if not self.nlp:
            logger.warning("SpaCy model not loaded. Cannot extract general keywords.")
            return []

        doc = self.nlp(text.lower())
        tokens = [token.text for token in doc if token.is_alpha and not token.is_stop and len(token.text) > 2]

        found_keywords = []
        for keyword in self.common_keywords_lower:
            if keyword in tokens or any(re.search(r'\b' + re.escape(keyword) + r'\b', token) for token in tokens):
                found_keywords.append(keyword)

        # You could also extract relevant noun chunks or entities here
        # E.g., for general domain keywords, not necessarily from your predefined list
        # For example, filtering noun chunks that are not skills but seem relevant:
        # found_keywords.extend([chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1 and chunk.text.lower() not in self.common_skills_lower])

        return sorted(list(set(found_keywords)))