"""
Home Page API Routes

Provides endpoints for dashboard data and home page functionality.
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from database.utils import get_db
from services.home_page_service import HomePageService
from utils.auth import verify_token
from models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/home", tags=["home"])
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to get current authenticated user ID
    """
    token = credentials.credentials
    payload = verify_token(token, "access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return user_id

@router.get("/dashboard")
async def get_dashboard_data(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard data for the authenticated user

    Returns:
        Dictionary containing all dashboard data including:
        - User stats (activities, time tracked, mood, energy, productivity)
        - Recent activities
        - Today's schedule
        - Goals progress
        - AI insights
        - Productivity trends
    """
    try:
        logger.info(f"Fetching dashboard data for user: {current_user_id}")

        # Create home page service
        home_service = HomePageService(db)

        # Get dashboard data
        dashboard_data = home_service.get_dashboard_data(current_user_id)

        logger.info(f"Successfully retrieved dashboard data for user: {current_user_id}")
        return {
            "success": True,
            "data": dashboard_data
        }

    except Exception as e:
        logger.error(f"Error fetching dashboard data for user {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard data"
        )

@router.get("/stats")
async def get_user_stats(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user statistics summary

    Returns:
        Dictionary containing user stats like activity counts, time tracked, etc.
    """
    try:
        logger.info(f"Fetching user stats for: {current_user_id}")

        home_service = HomePageService(db)
        dashboard_data = home_service.get_dashboard_data(current_user_id)

        return {
            "success": True,
            "data": dashboard_data["stats"]
        }

    except Exception as e:
        logger.error(f"Error fetching user stats for {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user statistics"
        )

@router.get("/recent-activities")
async def get_recent_activities(
    limit: int = 5,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user's recent activities

    Args:
        limit: Number of activities to return (default: 5)

    Returns:
        List of recent activities
    """
    try:
        logger.info(f"Fetching recent activities for user: {current_user_id}")

        home_service = HomePageService(db)
        recent_activities = home_service._get_recent_activities(current_user_id, limit)

        return {
            "success": True,
            "data": recent_activities
        }

    except Exception as e:
        logger.error(f"Error fetching recent activities for {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recent activities"
        )

@router.get("/insights")
async def get_ai_insights(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get AI-generated insights for the user

    Returns:
        List of personalized insights and recommendations
    """
    try:
        logger.info(f"Fetching AI insights for user: {current_user_id}")

        home_service = HomePageService(db)
        dashboard_data = home_service.get_dashboard_data(current_user_id)

        return {
            "success": True,
            "data": dashboard_data["ai_insights"]
        }

    except Exception as e:
        logger.error(f"Error fetching AI insights for {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch AI insights"
        )

@router.get("/schedule/today")
async def get_today_schedule(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get today's schedule for the user

    Returns:
        List of scheduled activities/tasks for today
    """
    try:
        logger.info(f"Fetching today's schedule for user: {current_user_id}")

        home_service = HomePageService(db)
        dashboard_data = home_service.get_dashboard_data(current_user_id)

        return {
            "success": True,
            "data": dashboard_data["today_schedule"]
        }

    except Exception as e:
        logger.error(f"Error fetching today's schedule for {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch today's schedule"
        )

@router.get("/productivity-trends")
async def get_productivity_trends(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get productivity trends and analytics

    Returns:
        Productivity trends data including daily activity counts and time tracking
    """
    try:
        logger.info(f"Fetching productivity trends for user: {current_user_id}")

        home_service = HomePageService(db)
        dashboard_data = home_service.get_dashboard_data(current_user_id)

        return {
            "success": True,
            "data": dashboard_data["productivity_trends"]
        }

    except Exception as e:
        logger.error(f"Error fetching productivity trends for {current_user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch productivity trends"
        )

@router.get("/demo")
async def get_demo_dashboard_data(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Demo dashboard endpoint that doesn't require authentication
    Uses a hardcoded demo user ID for testing

    Returns:
        Dictionary containing demo dashboard data from database
    """
    try:
        logger.info("Fetching demo dashboard data")

        # Use a demo user ID in UUID format - in production this would come from authentication
        demo_user_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

        # Create demo user if it doesn't exist
        demo_user = db.query(User).filter(User.id == demo_user_id).first()
        if not demo_user:
            demo_user = User(
                id=demo_user_id,
                name="Demo User",
                email="demo@elevateai.com",
                password_hash="demo_hash",  # Not used for demo
                is_active=True,
                is_verified=True
            )
            db.add(demo_user)
            db.commit()
            logger.info("Created demo user")

        # Create home page service
        home_service = HomePageService(db)

        # Get dashboard data for demo user
        dashboard_data = home_service.get_dashboard_data(demo_user_id)

        logger.info("Successfully retrieved demo dashboard data")
        return {
            "success": True,
            "data": dashboard_data
        }

    except Exception as e:
        logger.error(f"Error fetching demo dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch demo dashboard data"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the home page service

    Returns:
        Service health status
    """
    return {
        "success": True,
        "service": "home_page_service",
        "status": "healthy",
        "message": "Home page service is running"
    }
