"""Script to add must_ask field to the interview_questions table."""
import logging
from sqlalchemy import Column, Boolean
from sqlalchemy.sql import text
from app.database import engine, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_must_ask_field():
    """Add must_ask field to the interview_questions table."""
    db = SessionLocal()
    try:
        # Check if column already exists
        check_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='interview_questions' AND column_name='must_ask';
        """
        result = db.execute(text(check_sql)).fetchone()
        
        if result is None:
            # Add the column
            logger.info("Adding must_ask column to interview_questions table")
            add_sql = """
            ALTER TABLE interview_questions 
            ADD COLUMN must_ask BOOLEAN NOT NULL DEFAULT false;
            """
            db.execute(text(add_sql))
            db.commit()
            logger.info("Column added successfully")
        else:
            logger.info("must_ask column already exists")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding must_ask column: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_must_ask_field() 