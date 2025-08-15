"""
Database utility functions for Elevate AI backend
"""

from sqlalchemy.orm import Session
from database.database import SessionLocal, engine, Base
from models import (
    User, ActivityLog, AIInsight, Schedule, Goal, GoalProgress,
    ActivityTag, Tag, InsightAction, ScheduleTask, UserPreferences
)
from typing import Generator
import logging

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Used with FastAPI's Depends() for dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    This should be called during application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def init_database():
    """
    Initialize the database with tables and any required seed data.
    """
    try:
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def check_database_connection():
    """
    Check if database connection is working.
    Returns True if connection is successful, False otherwise.
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_user_by_email(db: Session, email: str) -> User:
    """
    Get user by email address.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> User:
    """
    Get user by ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: dict) -> User:
    """
    Create a new user in the database.
    """
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_last_login(db: Session, user_id: str):
    """
    Update user's last login timestamp.
    """
    from datetime import datetime, timezone
    
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
    return user


def get_user_activity_logs(db: Session, user_id: str, limit: int = 50):
    """
    Get user's activity logs with optional limit.
    """
    return db.query(ActivityLog).filter(
        ActivityLog.user_id == user_id
    ).order_by(ActivityLog.created_at.desc()).limit(limit).all()


def get_user_schedules(db: Session, user_id: str, limit: int = 30):
    """
    Get user's schedules with optional limit.
    """
    return db.query(Schedule).filter(
        Schedule.user_id == user_id
    ).order_by(Schedule.date.desc()).limit(limit).all()


def get_user_ai_insights(db: Session, user_id: str, limit: int = 20):
    """
    Get user's AI insights with optional limit.
    """
    return db.query(AIInsight).filter(
        AIInsight.user_id == user_id
    ).order_by(AIInsight.generated_at.desc()).limit(limit).all()


def get_user_statistics(db: Session, user_id: str) -> dict:
    """
    Get user statistics (total counts of activities, schedules, insights).
    """
    total_activities = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).count()
    total_schedules = db.query(Schedule).filter(Schedule.user_id == user_id).count()
    total_insights = db.query(AIInsight).filter(AIInsight.user_id == user_id).count()
    
    return {
        "total_activities": total_activities,
        "total_schedules": total_schedules,
        "total_insights": total_insights
    }


def cleanup_old_data(db: Session, days_to_keep: int = 90):
    """
    Clean up old data (older than specified days).
    This is useful for data retention policies.
    """
    from datetime import datetime, timezone, timedelta
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
    
    try:
        # Clean up old activity logs
        old_activities = db.query(ActivityLog).filter(
            ActivityLog.created_at < cutoff_date
        ).delete()
        
        # Clean up old AI insights
        old_insights = db.query(AIInsight).filter(
            AIInsight.generated_at < cutoff_date
        ).delete()
        
        # Clean up old schedules
        old_schedules = db.query(Schedule).filter(
            Schedule.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleaned up old data: {old_activities} activities, "
                   f"{old_insights} insights, {old_schedules} schedules")
        
        return {
            "activities_deleted": old_activities,
            "insights_deleted": old_insights,
            "schedules_deleted": old_schedules
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error cleaning up old data: {e}")
        raise


def create_user_with_preferences(db: Session, user_data: dict, preferences_data: dict = None) -> User:
    """
    Create a new user with default preferences.
    """
    # Create user
    db_user = User(**user_data)
    db.add(db_user)
    db.flush()  # Flush to get the user ID

    # Create default preferences
    if preferences_data is None:
        preferences_data = {}

    preferences_data["user_id"] = db_user.id
    db_preferences = UserPreferences(**preferences_data)
    db.add(db_preferences)

    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_with_relationships(db: Session, user_id: str, include_relationships: list = None):
    """
    Get user with specified relationships loaded.
    """
    from sqlalchemy.orm import joinedload

    query = db.query(User).filter(User.id == user_id)

    if include_relationships:
        for rel in include_relationships:
            if hasattr(User, rel):
                query = query.options(joinedload(getattr(User, rel)))

    return query.first()


def get_user_tags(db: Session, user_id: str) -> list:
    """
    Get all tags for a user.
    """
    return db.query(Tag).filter(Tag.user_id == user_id).all()


def create_or_get_tag(db: Session, user_id: str, tag_name: str, color: str = None) -> Tag:
    """
    Create a new tag or get existing one.
    """
    # Try to get existing tag
    existing_tag = db.query(Tag).filter(
        Tag.user_id == user_id,
        Tag.name == tag_name
    ).first()

    if existing_tag:
        return existing_tag

    # Create new tag
    new_tag = Tag(
        user_id=user_id,
        name=tag_name,
        color=color
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag


def get_user_goals_with_progress(db: Session, user_id: str, active_only: bool = True):
    """
    Get user's goals with their progress.
    """
    from sqlalchemy.orm import joinedload

    query = db.query(Goal).options(
        joinedload(Goal.goal_progress)
    ).filter(Goal.user_id == user_id)

    if active_only:
        query = query.filter(Goal.is_active == True)

    return query.all()


def update_goal_progress(db: Session, goal_id: str, user_id: str, value: float, notes: str = None):
    """
    Add progress entry to a goal and update current value.
    """
    # Create progress entry
    progress_entry = GoalProgress(
        goal_id=goal_id,
        user_id=user_id,
        value=value,
        notes=notes
    )
    db.add(progress_entry)

    # Update goal's current value
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if goal:
        goal.current_value = value

        # Check if goal is completed
        if value >= goal.target_value and not goal.is_completed:
            from datetime import datetime, timezone
            goal.is_completed = True
            goal.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(progress_entry)
    return progress_entry
