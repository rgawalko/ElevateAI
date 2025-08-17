"""
Database migration to add chronotype_data field to users table
"""

import psycopg2
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def add_chronotype_field():
    """Add chronotype_data JSON column to users table"""
    try:
        # Get database connection from environment
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set")

        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='chronotype_data'
        """)
        
        if cursor.fetchone():
            logger.info("chronotype_data column already exists")
            return True
        
        # Add the column
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN chronotype_data JSON
        """)
        
        conn.commit()
        logger.info("Successfully added chronotype_data column to users table")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error adding chronotype_data column: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    add_chronotype_field()
