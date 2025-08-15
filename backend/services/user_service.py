"""
User Service

Handles all user-related business logic including authentication,
profile management, and user statistics.
"""

from sqlalchemy.orm import Session, joinedload
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import uuid

from .base_service import BaseService
from models import User, UserPreferences, ActivityLog, Goal, Schedule, AIInsight
from utils.auth import hash_password, verify_password, validate_password_strength


class UserService(BaseService):
    """
    Service for user management operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Create a new user with default preferences.
        """
        try:
            # Validate password if provided
            if 'password' in user_data:
                password_validation = validate_password_strength(user_data['password'])
                if not password_validation['is_valid']:
                    self.logger.error(f"Password validation failed: {password_validation['errors']}")
                    return None
                
                # Hash password
                user_data['password_hash'] = hash_password(user_data['password'])
                del user_data['password']
            
            # Create user
            user = User(**user_data)
            self.db.add(user)
            self.db.flush()  # Get user ID
            
            # Create default preferences
            preferences = UserPreferences(user_id=user.id)
            self.db.add(preferences)
            
            self.db.commit()
            self.db.refresh(user)
            
            self.logger.info(f"Created user: {user.email}")
            return user
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        """
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    def get_user_with_preferences(self, user_id: str) -> Optional[User]:
        """
        Get user with preferences loaded.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            return self.db.query(User).options(
                joinedload(User.preferences)
            ).filter(User.id == uuid_id).first()
        except Exception as e:
            self.logger.error(f"Error getting user with preferences: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        """
        try:
            user = self.get_user_by_email(email)
            if not user:
                return None
            
            if not user.is_active:
                self.logger.warning(f"Inactive user attempted login: {email}")
                return None
            
            if not verify_password(password, user.password_hash):
                return None
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            self.db.commit()
            
            return user
            
        except Exception as e:
            self.logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """
        Update user profile information.
        """
        try:
            user = self.get_by_id(User, user_id)
            if not user:
                return None
            
            # Remove fields that shouldn't be updated directly
            restricted_fields = ['id', 'password_hash', 'created_at']
            for field in restricted_fields:
                update_data.pop(field, None)
            
            return self.update(user, update_data)
            
        except Exception as e:
            self.logger.error(f"Error updating user profile: {e}")
            return None
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user password after validating current password.
        """
        try:
            user = self.get_by_id(User, user_id)
            if not user:
                return False
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                self.logger.warning(f"Invalid current password for user {user_id}")
                return False
            
            # Validate new password
            password_validation = validate_password_strength(new_password)
            if not password_validation['is_valid']:
                self.logger.error(f"New password validation failed: {password_validation['errors']}")
                return False
            
            # Update password
            user.password_hash = hash_password(new_password)
            return self.safe_commit()
            
        except Exception as e:
            self.logger.error(f"Error changing password: {e}")
            return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate user account (soft delete).
        """
        try:
            user = self.get_by_id(User, user_id)
            if not user:
                return False
            
            user.is_active = False
            return self.safe_commit()
            
        except Exception as e:
            self.logger.error(f"Error deactivating user: {e}")
            return False
    
    def reactivate_user(self, user_id: str) -> bool:
        """
        Reactivate user account.
        """
        try:
            user = self.get_by_id(User, user_id)
            if not user:
                return False
            
            user.is_active = True
            return self.safe_commit()
            
        except Exception as e:
            self.logger.error(f"Error reactivating user: {e}")
            return False
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user statistics.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            
            # Get counts
            activity_count = self.db.query(ActivityLog).filter(ActivityLog.user_id == uuid_id).count()
            goal_count = self.db.query(Goal).filter(Goal.user_id == uuid_id).count()
            schedule_count = self.db.query(Schedule).filter(Schedule.user_id == uuid_id).count()
            insight_count = self.db.query(AIInsight).filter(AIInsight.user_id == uuid_id).count()
            
            # Get completed goals
            completed_goals = self.db.query(Goal).filter(
                Goal.user_id == uuid_id,
                Goal.is_completed == True
            ).count()
            
            # Get recent activity (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_activities = self.db.query(ActivityLog).filter(
                ActivityLog.user_id == uuid_id,
                ActivityLog.created_at >= thirty_days_ago
            ).count()
            
            # Get AI-generated schedules
            ai_schedules = self.db.query(Schedule).filter(
                Schedule.user_id == uuid_id,
                Schedule.generated_by_ai == True
            ).count()
            
            return {
                "total_activities": activity_count,
                "total_goals": goal_count,
                "completed_goals": completed_goals,
                "total_schedules": schedule_count,
                "ai_generated_schedules": ai_schedules,
                "total_insights": insight_count,
                "recent_activities": recent_activities,
                "goal_completion_rate": (completed_goals / goal_count * 100) if goal_count > 0 else 0,
                "activity_frequency": recent_activities / 30.0  # per day
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user statistics: {e}")
            return {}
    
    def update_user_preferences(self, user_id: str, preferences_data: Dict[str, Any]) -> Optional[UserPreferences]:
        """
        Update user preferences.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            preferences = self.db.query(UserPreferences).filter(
                UserPreferences.user_id == uuid_id
            ).first()
            
            if not preferences:
                # Create preferences if they don't exist
                preferences_data['user_id'] = uuid_id
                preferences = UserPreferences(**preferences_data)
                self.db.add(preferences)
            else:
                # Update existing preferences
                for field, value in preferences_data.items():
                    if hasattr(preferences, field) and field != 'user_id':
                        setattr(preferences, field, value)
            
            self.db.commit()
            self.db.refresh(preferences)
            return preferences
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating user preferences: {e}")
            return None
    
    def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Get user preferences.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            return self.db.query(UserPreferences).filter(
                UserPreferences.user_id == uuid_id
            ).first()
        except Exception as e:
            self.logger.error(f"Error getting user preferences: {e}")
            return None
