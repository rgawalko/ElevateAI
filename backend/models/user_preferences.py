from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone


class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key (One-to-One with User)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Notification Preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    daily_summary = Column(Boolean, default=True)
    weekly_report = Column(Boolean, default=True)
    insight_notifications = Column(Boolean, default=True)
    goal_reminders = Column(Boolean, default=True)
    
    # Schedule Preferences
    work_start_time = Column(String(5), default="09:00")  # HH:MM format
    work_end_time = Column(String(5), default="17:00")    # HH:MM format
    lunch_break_duration = Column(Integer, default=60)    # minutes
    short_break_duration = Column(Integer, default=15)    # minutes
    long_break_duration = Column(Integer, default=30)     # minutes
    max_consecutive_work_hours = Column(Integer, default=4)
    
    # AI Preferences
    ai_suggestions_enabled = Column(Boolean, default=True)
    auto_schedule_generation = Column(Boolean, default=False)
    insight_frequency = Column(String(20), default="weekly")  # daily, weekly, monthly
    productivity_tracking = Column(Boolean, default=True)
    
    # Privacy Preferences
    data_sharing = Column(Boolean, default=False)
    analytics_tracking = Column(Boolean, default=True)
    
    # Theme and Display
    theme = Column(String(20), default="light")  # light, dark, auto
    language = Column(String(10), default="en")
    
    # Custom Settings (flexible JSON field)
    custom_settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="preferences", uselist=False)
    
    def __repr__(self):
        return f"<UserPreferences(id={self.id}, user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert user preferences to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "daily_summary": self.daily_summary,
            "weekly_report": self.weekly_report,
            "insight_notifications": self.insight_notifications,
            "goal_reminders": self.goal_reminders,
            "work_start_time": self.work_start_time,
            "work_end_time": self.work_end_time,
            "lunch_break_duration": self.lunch_break_duration,
            "short_break_duration": self.short_break_duration,
            "long_break_duration": self.long_break_duration,
            "max_consecutive_work_hours": self.max_consecutive_work_hours,
            "ai_suggestions_enabled": self.ai_suggestions_enabled,
            "auto_schedule_generation": self.auto_schedule_generation,
            "insight_frequency": self.insight_frequency,
            "productivity_tracking": self.productivity_tracking,
            "data_sharing": self.data_sharing,
            "analytics_tracking": self.analytics_tracking,
            "theme": self.theme,
            "language": self.language,
            "custom_settings": self.custom_settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_custom_setting(self, key: str, value):
        """Update a custom setting"""
        if self.custom_settings is None:
            self.custom_settings = {}
        self.custom_settings[key] = value
    
    def get_custom_setting(self, key: str, default=None):
        """Get a custom setting value"""
        if self.custom_settings is None:
            return default
        return self.custom_settings.get(key, default)
