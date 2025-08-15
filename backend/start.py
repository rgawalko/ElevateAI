#!/usr/bin/env python3
"""
Startup script for Elevate AI Backend
This script provides a convenient way to start the backend server with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file."""
    try:
        from dotenv import load_dotenv
        backend_dir = Path(__file__).parent
        env_file = backend_dir / ".env"

        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"✅ Loaded environment from {env_file}")
        else:
            logger.warning(f"⚠️  No .env file found at {env_file}")
    except ImportError:
        logger.warning("⚠️  python-dotenv not installed. Using system environment variables.")


def check_database_connection():
    """Check database connection and initialize if needed."""
    try:
        # Add backend directory to path
        backend_dir = Path(__file__).parent
        sys.path.insert(0, str(backend_dir))

        from database.utils import check_database_connection, init_database

        logger.info("🔍 Checking database connection...")
        if check_database_connection():
            logger.info("✅ Database connection successful")

            # Initialize tables if needed
            logger.info("🔄 Initializing database tables...")
            init_database()
            logger.info("✅ Database tables ready")
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database setup error: {e}")
        return False


def main():
    """
    Main startup function
    """
    print("🚀 Starting Elevate AI Backend...")

    # Load environment variables
    load_environment()

    # Get the directory where this script is located
    backend_dir = Path(__file__).parent
    api_dir = backend_dir / "API"

    # Set environment variables if not already set
    if not os.getenv("DATABASE_URL"):
        logger.warning("⚠️  DATABASE_URL not set, using SQLite default")
        os.environ["DATABASE_URL"] = "sqlite:///./elevate_ai.db"

    if not os.getenv("JWT_SECRET_KEY"):
        logger.warning("⚠️  JWT_SECRET_KEY not set, using development key")
        os.environ["JWT_SECRET_KEY"] = "dev-secret-key-change-in-production"

    # Set debug mode for development
    if not os.getenv("DEBUG"):
        os.environ["DEBUG"] = "true"

    # Check database connection
    if not check_database_connection():
        logger.error("❌ Cannot start server - database connection failed")
        logger.info("💡 Try running: python setup_database.py")
        sys.exit(1)

    # Change to the API directory
    os.chdir(api_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🗄️  Database: {os.getenv('DATABASE_URL')}")
    print(f"🔧 Debug mode: {os.getenv('DEBUG')}")
    print(f"🌐 Server will start on: http://localhost:8000")
    print(f"📚 API docs will be available at: http://localhost:8000/docs")
    print()
    
    try:
        # Start the server using uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
