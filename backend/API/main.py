"""
Elevate AI Backend - FastAPI Application
Main entry point for the Elevate AI productivity and wellness application backend.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Add the parent directory to the Python path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.utils import init_database, check_database_connection
from routes import (
    auth_router,
    users_router,
    activities_router,
    schedules_router,
    insights_router,
    goals_router,
    chatbot_router,
    chronotype_router,
    home_router,
    test_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager - handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Elevate AI Backend...")

    try:
        # Check database connection
        if not check_database_connection():
            logger.error("❌ Database connection failed!")
            raise Exception("Database connection failed")

        # Initialize database tables
        init_database()
        logger.info("✅ Database initialized successfully")

        logger.info("🎉 Elevate AI Backend started successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Elevate AI Backend...")


# Create FastAPI application
app = FastAPI(
    title="Elevate AI Backend",
    description="Backend API for Elevate AI - A productivity and wellness application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:5173",  # Vite development server (default)
        "http://localhost:5174",  # Vite development server (current)
        "http://localhost:8000",  # Backend port 8000
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Health check
    """
    return {
        "message": "Elevate AI Backend is running! 🚀",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check endpoint
    """
    from datetime import datetime
    import os

    try:
        # Check database connection
        db_healthy = check_database_connection()

        # Get database URL (without credentials)
        db_url = os.getenv("DATABASE_URL", "")
        db_type = "unknown"
        if db_url.startswith("postgresql://"):
            db_type = "PostgreSQL"
        elif db_url.startswith("sqlite://"):
            db_type = "SQLite"

        # Get additional database info
        db_info = {
            "type": db_type,
            "connected": db_healthy,
            "pool_size": os.getenv("DB_POOL_SIZE", "10"),
            "max_overflow": os.getenv("DB_MAX_OVERFLOW", "20")
        }

        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": db_info,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "environment": os.getenv("DEBUG", "false").lower() == "true" and "development" or "production"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Include API routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(activities_router, prefix="/api")
app.include_router(schedules_router, prefix="/api")
app.include_router(insights_router, prefix="/api")
app.include_router(goals_router, prefix="/api")
app.include_router(chronotype_router, prefix="/api")
app.include_router(chatbot_router)
app.include_router(home_router)
app.include_router(test_router, prefix="/api")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )


# Application entry point
if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"🌟 Starting Elevate AI Backend on {host}:{port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"📚 API Documentation: http://{host}:{port}/docs")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )
