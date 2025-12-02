import asyncio
import os
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configurations
# MariaDB (Source) - using pymysql for sync connection or aiomysql if needed, but let's use sync for migration script simplicity if possible, 
# or async if we want to reuse project patterns. 
# Actually, for a one-off script, sync is often easier, but we installed asyncpg. 
# Let's use the installed drivers. We added pymysql and psycopg2-binary for this script specifically.

# Source: MariaDB
MARIADB_USER = "memo_user"
MARIADB_PASSWORD = "phoenix"
MARIADB_HOST = "localhost"
MARIADB_PORT = "3307" # Host port
MARIADB_DB = "memo_app"
MARIADB_URL = f"mysql+pymysql://{MARIADB_USER}:{MARIADB_PASSWORD}@{MARIADB_HOST}:{MARIADB_PORT}/{MARIADB_DB}"

# Destination: Postgres (sgcc-db)
POSTGRES_USER = "admin"
POSTGRES_PASSWORD = "82292" # From docker inspect
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432" # Host port
POSTGRES_DB = "sgcc-backend-db"
POSTGRES_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def migrate_data():
    logger.info("Starting data migration...")

    # Connect to MariaDB
    try:
        mariadb_engine = sqlalchemy.create_engine(MARIADB_URL)
        mariadb_conn = mariadb_engine.connect()
        logger.info("Connected to MariaDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MariaDB: {e}")
        return

    # Connect to Postgres
    try:
        postgres_engine = sqlalchemy.create_engine(POSTGRES_URL)
        postgres_conn = postgres_engine.connect()
        logger.info("Connected to Postgres.")
    except Exception as e:
        logger.error(f"Failed to connect to Postgres: {e}")
        mariadb_conn.close()
        return

    # 1. Fetch data from MariaDB
    try:
        logger.info("Fetching memos from MariaDB...")
        result = mariadb_conn.execute(text("SELECT * FROM memos"))
        memos = result.fetchall()
        logger.info(f"Found {len(memos)} memos.")
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        mariadb_conn.close()
        postgres_conn.close()
        return

    # 2. Insert data into Postgres
    # We need to ensure the table exists. The app creates it, but we might be running this before the app runs against Postgres.
    # Let's assume the table schema is compatible. We might need to create it if it doesn't exist.
    # For simplicity, we'll assume the user runs the app once or we create the table here.
    # Actually, the implementation plan said "The app's lifespan creates tables". 
    # But we need to insert data NOW. 
    # Let's define the table schema using SQLAlchemy Core to ensure it exists.

    metadata = sqlalchemy.MetaData()
    memos_table = sqlalchemy.Table(
        "memos",
        metadata,
        sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
        sqlalchemy.Column("title", sqlalchemy.String(100), nullable=False),
        sqlalchemy.Column("content", sqlalchemy.Text, nullable=False),
        sqlalchemy.Column("tags", sqlalchemy.JSON, nullable=True),
        sqlalchemy.Column("priority", sqlalchemy.Integer, nullable=False, default=2),
        sqlalchemy.Column("category", sqlalchemy.String(50), nullable=True),
        sqlalchemy.Column("is_archived", sqlalchemy.Boolean, nullable=False, default=False),
        sqlalchemy.Column("is_favorite", sqlalchemy.Boolean, nullable=False, default=False),
        sqlalchemy.Column("author", sqlalchemy.String(100), nullable=True),
        sqlalchemy.Column("created_at", sqlalchemy.DateTime),
        sqlalchemy.Column("updated_at", sqlalchemy.DateTime),
    )

    try:
        logger.info("Ensuring 'memos' table exists in Postgres...")
        metadata.create_all(postgres_engine)
        
        logger.info("Inserting memos into Postgres...")
        # We need to handle the fact that 'tags' in MariaDB might be JSON string or actual JSON depending on driver/storage.
        # In MariaDB it was JSON type.
        
        import json
        for memo in memos:
            # Check if memo already exists to avoid duplicates if run multiple times
            exists = postgres_conn.execute(text("SELECT 1 FROM memos WHERE id = :id"), {"id": memo.id}).fetchone()
            if exists:
                logger.info(f"Memo {memo.id} already exists. Skipping.")
                continue

            # Handle tags: Ensure it's a list, not a string representation
            tags_val = memo.tags
            if isinstance(tags_val, str):
                try:
                    tags_val = json.loads(tags_val)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse tags for memo {memo.id}: {tags_val}. Using empty list.")
                    tags_val = []
            elif tags_val is None:
                tags_val = []

            # Prepare data dictionary
            data = {
                "id": memo.id,
                "title": memo.title,
                "content": memo.content,
                "tags": tags_val, 
                "priority": memo.priority,
                "category": memo.category,
                "is_archived": memo.is_archived,
                "is_favorite": memo.is_favorite,
                "author": memo.author,
                "created_at": memo.created_at,
                "updated_at": memo.updated_at
            }
            
            postgres_conn.execute(memos_table.insert().values(**data))
        
        postgres_conn.commit()
        logger.info("Migration completed successfully.")

    except Exception as e:
        logger.error(f"Error during insertion: {e}")
        postgres_conn.rollback()
    finally:
        mariadb_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    migrate_data()
