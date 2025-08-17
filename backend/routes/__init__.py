"""
API Routes for Elevate AI Backend
"""

from .auth import router as auth_router
from .users import router as users_router
from .activities import router as activities_router
from .schedules import router as schedules_router
from .insights import router as insights_router
from .goals import router as goals_router
from .chatbot import router as chatbot_router
from .chronotype import router as chronotype_router
from .home import router as home_router
from .test_routes import router as test_router

__all__ = [
    "auth_router",
    "users_router",
    "activities_router",
    "schedules_router",
    "insights_router",
    "goals_router",
    "chatbot_router",
    "chronotype_router",
    "home_router",
    "test_router"
]
