from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone


class ScheduleTask(Base):
    __tablename__ = "schedule_tasks"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("schedules.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Task Information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Time Information
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    estimated_duration = Column(Integer, nullable=False)  # in minutes
    actual_duration = Column(Integer, nullable=True)  # in minutes
    
    # Task Properties
    priority = Column(Integer, default=3)  # 1 = highest, 5 = lowest
    is_completed = Column(Boolean, default=False)
    is_break = Column(Boolean, default=False)
    
    # Completion Information
    completion_notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    schedule = relationship("Schedule", back_populates="schedule_tasks")
    user = relationship("User", back_populates="schedule_tasks")
    
    def __repr__(self):
        return f"<ScheduleTask(id={self.id}, title={self.title}, schedule_id={self.schedule_id})>"
    
    @property
    def duration_minutes(self) -> int:
        """Calculate duration in minutes from start and end time"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return self.estimated_duration or 0
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if self.is_completed or not self.end_time:
            return False
        return datetime.now(timezone.utc) > self.end_time.replace(tzinfo=timezone.utc)
    
    def mark_completed(self, notes: str = None, actual_duration: int = None):
        """Mark task as completed"""
        self.is_completed = True
        self.completed_at = datetime.now(timezone.utc)
        if notes:
            self.completion_notes = notes
        if actual_duration:
            self.actual_duration = actual_duration
    
    def to_dict(self):
        """Convert schedule task to dictionary"""
        return {
            "id": str(self.id),
            "schedule_id": str(self.schedule_id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "is_completed": self.is_completed,
            "is_break": self.is_break,
            "is_overdue": self.is_overdue,
            "completion_notes": self.completion_notes,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
