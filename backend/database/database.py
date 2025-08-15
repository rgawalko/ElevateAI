from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# PostgreSQL database URL - required environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Database configuration from environment
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Create PostgreSQL engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before use
    echo=os.getenv("DEBUG", "False").lower() == "true"
)
logger.info(f"Using PostgreSQL database with pool_size={DB_POOL_SIZE}, max_overflow={DB_MAX_OVERFLOW}")

# Add connection event listeners for PostgreSQL
@event.listens_for(engine, "connect")
def set_postgresql_params(dbapi_connection, _connection_record):
    """Set PostgreSQL connection parameters."""
    with dbapi_connection.cursor() as cursor:
        # Set timezone to UTC
        cursor.execute("SET timezone TO 'UTC'")

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Used with FastAPI's Depends() for dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
