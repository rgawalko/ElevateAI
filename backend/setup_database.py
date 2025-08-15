#!/usr/bin/env python3
"""
Database setup script for Elevate AI

This script helps you set up and initialize the PostgreSQL database.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_database_url(database_url: str) -> dict:
    """Parse DATABASE_URL into components."""
    # Example: postgresql://username:password@localhost:5432/database_name
    if not database_url.startswith('postgresql://'):
        raise ValueError("DATABASE_URL must start with 'postgresql://'")
    
    # Remove protocol
    url = database_url.replace('postgresql://', '')
    
    # Split user info and host info
    if '@' in url:
        user_info, host_info = url.split('@', 1)
        if ':' in user_info:
            username, password = user_info.split(':', 1)
        else:
            username = user_info
            password = ''
    else:
        raise ValueError("DATABASE_URL must include username@host format")
    
    # Split host and database
    if '/' in host_info:
        host_port, database = host_info.split('/', 1)
    else:
        host_port = host_info
        database = 'elevate_ai'
    
    # Split host and port
    if ':' in host_port:
        host, port = host_port.split(':', 1)
        port = int(port)
    else:
        host = host_port
        port = 5432
    
    return {
        'username': username,
        'password': password,
        'host': host,
        'port': port,
        'database': database
    }


def check_postgresql_connection(db_config: dict) -> bool:
    """Check if PostgreSQL server is running and accessible."""
    try:
        # Connect to PostgreSQL server (not specific database)
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['username'],
            password=db_config['password'],
            database='postgres'  # Connect to default postgres database
        )
        conn.close()
        logger.info("✅ PostgreSQL server connection successful")
        return True
    except psycopg2.OperationalError as e:
        logger.error(f"❌ PostgreSQL server connection failed: {e}")
        return False


def database_exists(db_config: dict) -> bool:
    """Check if the target database exists."""
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['username'],
            password=db_config['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_config['database'],))
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        
        return exists
    except Exception as e:
        logger.error(f"Error checking database existence: {e}")
        return False


def create_database(db_config: dict) -> bool:
    """Create the database if it doesn't exist."""
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['username'],
            password=db_config['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f'CREATE DATABASE "{db_config["database"]}"')
        logger.info(f"✅ Database '{db_config['database']}' created successfully")
        
        cursor.close()
        conn.close()
        return True
    except psycopg2.errors.DuplicateDatabase:
        logger.info(f"ℹ️  Database '{db_config['database']}' already exists")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        return False


def test_database_connection(database_url: str) -> bool:
    """Test connection to the target database."""
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        logger.info(f"✅ Database connection successful. PostgreSQL version: {version}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def initialize_tables():
    """Initialize database tables using SQLAlchemy."""
    try:
        # Add the backend directory to Python path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from database.utils import init_database, check_database_connection
        
        if check_database_connection():
            logger.info("🔄 Initializing database tables...")
            init_database()
            logger.info("✅ Database tables initialized successfully")
            return True
        else:
            logger.error("❌ Cannot initialize tables - database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Error initializing tables: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Elevate AI Database Setup")
    print("=" * 40)
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not found")
        logger.info("Please set DATABASE_URL in your .env file")
        logger.info("Example: DATABASE_URL=postgresql://username:password@localhost:5432/elevate_ai")
        return False
    
    logger.info(f"📊 Database URL: {database_url}")
    
    # Parse database configuration
    try:
        db_config = parse_database_url(database_url)
        logger.info(f"🔧 Database config: {db_config['username']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    except Exception as e:
        logger.error(f"❌ Error parsing DATABASE_URL: {e}")
        return False
    
    # Step 1: Check PostgreSQL server connection
    logger.info("\n📡 Step 1: Checking PostgreSQL server connection...")
    if not check_postgresql_connection(db_config):
        logger.error("❌ Setup failed: Cannot connect to PostgreSQL server")
        logger.info("Please ensure:")
        logger.info("  1. PostgreSQL is installed and running")
        logger.info("  2. Username and password are correct")
        logger.info("  3. Host and port are accessible")
        return False
    
    # Step 2: Check/Create database
    logger.info("\n🗄️  Step 2: Checking database existence...")
    if database_exists(db_config):
        logger.info(f"ℹ️  Database '{db_config['database']}' already exists")
    else:
        logger.info(f"🔄 Creating database '{db_config['database']}'...")
        if not create_database(db_config):
            logger.error("❌ Setup failed: Cannot create database")
            return False
    
    # Step 3: Test database connection
    logger.info("\n🔗 Step 3: Testing database connection...")
    if not test_database_connection(database_url):
        logger.error("❌ Setup failed: Cannot connect to target database")
        return False
    
    # Step 4: Initialize tables
    logger.info("\n📋 Step 4: Initializing database tables...")
    if not initialize_tables():
        logger.error("❌ Setup failed: Cannot initialize tables")
        return False
    
    # Success!
    print("\n" + "=" * 40)
    print("🎉 Database setup completed successfully!")
    print("=" * 40)
    print(f"✅ Database: {db_config['database']}")
    print(f"✅ Host: {db_config['host']}:{db_config['port']}")
    print(f"✅ Tables: Initialized")
    print("\n🚀 You can now start the backend server:")
    print("   cd backend")
    print("   python start.py")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
