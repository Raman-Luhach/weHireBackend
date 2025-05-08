"""Script to update existing interview categories and questions with job_id values."""
import logging
from sqlalchemy import update
from app.database import SessionLocal
from app.models import InterviewCategory, InterviewQuestion, Job

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_interview_data():
    """Update existing interview categories and questions with job_id=1."""
    db = SessionLocal()
    try:
        # Get the first job id to use as default
        first_job = db.query(Job).first()
        if not first_job:
            logger.error("No jobs found in the database. Please create at least one job first.")
            return
        
        job_id = first_job.id
        logger.info(f"Using job_id={job_id} for existing records")
        
        # Update all interview categories with NULL job_id
        null_categories = db.query(InterviewCategory).filter(InterviewCategory.job_id.is_(None)).all()
        logger.info(f"Found {len(null_categories)} categories with NULL job_id")
        
        if null_categories:
            for category in null_categories:
                category.job_id = job_id
            db.commit()
            logger.info(f"Updated {len(null_categories)} categories with job_id={job_id}")
        
        # Update all interview questions with NULL job_id
        null_questions = db.query(InterviewQuestion).filter(InterviewQuestion.job_id.is_(None)).all()
        logger.info(f"Found {len(null_questions)} questions with NULL job_id")
        
        if null_questions:
            for question in null_questions:
                question.job_id = job_id
            db.commit()
            logger.info(f"Updated {len(null_questions)} questions with job_id={job_id}")
        
        logger.info("Database update completed successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_interview_data() 