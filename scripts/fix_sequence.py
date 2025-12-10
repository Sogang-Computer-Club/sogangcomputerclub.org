import asyncio
import os
import sqlalchemy
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
POSTGRES_USER = "admin"
POSTGRES_PASSWORD = "82292" # From docker inspect (as seen in migrate_db.py)
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "sgcc-backend-db"
POSTGRES_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def fix_sequence():
    logger.info("Starting sequence fix...")

    try:
        engine = sqlalchemy.create_engine(POSTGRES_URL)
        conn = engine.connect()
        logger.info("Connected to Postgres.")
        
        # Get the max id
        result = conn.execute(text("SELECT MAX(id) FROM memos"))
        max_id = result.scalar()
        
        if max_id is None:
            max_id = 0
            
        logger.info(f"Current max id is {max_id}")
        
        # Reset the sequence
        # The sequence name is usually table_column_seq, so 'memos_id_seq'
        next_val = max_id + 1
        logger.info(f"Resetting sequence to {next_val}...")
        
        conn.execute(text(f"ALTER SEQUENCE memos_id_seq RESTART WITH {next_val}"))
        conn.commit()
        
        logger.info("Sequence reset successfully.")
        
    except Exception as e:
        logger.error(f"Error fixing sequence: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_sequence()
