"""Initialize the database with Alembic."""
import os
import sys
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Create the initial migration and apply it."""
    try:
        # Make sure we're in the correct directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(current_dir)
        
        # Make sure versions directory exists
        os.makedirs("alembic/versions", exist_ok=True)
        
        # Set proper permissions
        if sys.platform != "win32":  # Skip on Windows
            try:
                os.chmod("alembic/versions", 0o755)
            except Exception as e:
                logger.warning(f"Could not set permissions: {e}")
        
        logger.info("Creating initial migration...")
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)
        
        logger.info("Applying migration...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db() 