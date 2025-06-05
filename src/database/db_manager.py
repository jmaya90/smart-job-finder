import sqlite3
import logging
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DBManager:
    """
    Manages SQLite database connections and operations for job data.
    Each operation gets its own connection to handle Streamlit's threading model.
    """
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.create_tables() # Ensure tables exist on init
        logger.info(f"DBManager initialized for database: {self.db_path}")

    def _get_connection(self):
        """Internal method to get a new database connection."""
        try:
            # Use check_same_thread=False for Streamlit's multi-threading context
            # This is generally safe for read-heavy apps and avoids the ProgrammingError
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row # Allows accessing columns by name
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            return None

    def create_tables(self):
        """Creates the 'jobs' table if it doesn't exist."""
        with self._get_connection() as conn: # Use 'with' for auto-closing
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS jobs (
                            job_id TEXT PRIMARY KEY,
                            job_title TEXT,
                            company_name TEXT,
                            location TEXT,
                            job_description TEXT,
                            job_url TEXT,
                            employer_website TEXT,
                            job_employment_type TEXT,
                            job_posted_at_datetime_utc TEXT,
                            status TEXT DEFAULT 'new',
                            retrieved_at TEXT DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    conn.commit()
                    logger.info("Table 'jobs' created or already exists.")
                except sqlite3.Error as e:
                    logger.error(f"Error creating table: {e}")
            else:
                logger.error("Could not get a database connection to create tables.")


    def insert_job(self, job_data: dict) -> bool:
        """Inserts a new job into the database. Returns True if inserted, False if duplicate."""
        job_id = job_data.get('job_id')
        if not job_id:
            logger.warning("Attempted to insert job with no job_id.")
            return False

        with self._get_connection() as conn:
            if conn:
                try:
                    cursor = conn.cursor()
                    # Use INSERT OR IGNORE to handle duplicates gracefully
                    cursor.execute("""
                        INSERT OR IGNORE INTO jobs (
                            job_id, job_title, company_name, location,
                            job_description, job_url, employer_website,
                            job_employment_type, job_posted_at_datetime_utc
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        job_data.get('job_id'),
                        job_data.get('job_title'),
                        job_data.get('company_name'),
                        job_data.get('job_location'), # Note: JSearch API uses 'job_location'
                        job_data.get('job_description'),
                        job_data.get('job_apply_link'), # Note: JSearch API uses 'job_apply_link'
                        job_data.get('employer_website'),
                        job_data.get('job_employment_type'),
                        job_data.get('job_posted_at_datetime_utc')
                    ))
                    if cursor.rowcount > 0:
                        conn.commit()
                        logger.info(f"Inserted job: {job_data.get('job_title')} (ID: {job_id})")
                        return True
                    else:
                        logger.debug(f"Job with ID: {job_id} already exists. Skipping insertion.") # Use DEBUG for less verbose
                        return False
                except sqlite3.Error as e:
                    logger.error(f"Error inserting job {job_id}: {e}")
                    return False
            else:
                logger.error(f"Could not get a database connection to insert job {job_id}.")
                return False

    def get_all_jobs(self) -> list[dict]:
        """Retrieves all jobs from the database."""
        with self._get_connection() as conn:
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM jobs")
                    jobs = [dict(row) for row in cursor.fetchall()]
                    logger.info(f"Retrieved {len(jobs)} jobs from the database.")
                    return jobs
                except sqlite3.Error as e:
                    logger.error(f"Error retrieving all jobs: {e}")
                    return []
            else:
                logger.error("Could not get a database connection to retrieve all jobs.")
                return []

    def get_job_by_id(self, job_id: str) -> dict | None:
        """Retrieves a single job by its ID."""
        with self._get_connection() as conn:
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
                    job = cursor.fetchone()
                    if job:
                        logger.info(f"Retrieved job with ID: {job_id}")
                        return dict(job)
                    else:
                        logger.info(f"No job found with ID: {job_id}")
                        return None
                except sqlite3.Error as e:
                    logger.error(f"Error retrieving job {job_id}: {e}")
                    return None
            else:
                logger.error(f"Could not get a database connection to retrieve job {job_id}.")
                return None

    def update_job_status(self, job_id: str, new_status: str) -> bool:
        """Updates the status of a job."""
        with self._get_connection() as conn:
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE jobs
                        SET status = ?
                        WHERE job_id = ?
                    """, (new_status, job_id))
                    conn.commit()
                    if cursor.rowcount > 0:
                        logger.info(f"Updated status for job {job_id} to '{new_status}'.")
                        return True
                    else:
                        logger.warning(f"No job found with ID: {job_id} to update status.")
                        return False
                except sqlite3.Error as e:
                    logger.error(f"Error updating status for job {job_id}: {e}")
                    return False
            else:
                logger.error(f"Could not get a database connection to update job status for {job_id}.")
                return False

    # Remove the explicit close method from here, as 'with' handles it.
    # def close(self):
    #     """Closes the database connection."""
    #     if self.conn:
    #         self.conn.close()
    #         logger.info("Database connection closed.")