from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone


class Goal(Base):
    __tablename__ = "goals"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Goal Information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # health, productivity, learning, etc.
    
    # Goal Metrics
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    unit = Column(String(50), nullable=False)  # hours, count, percentage, etc.
    
    # Goal Status
    is_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Dates
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    deadline = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="goals")
    goal_progress = relationship("GoalProgress", back_populates="goal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Goal(id={self.id}, title={self.title}, progress={self.current_value}/{self.target_value})>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage"""
        if self.target_value == 0:
            return 0.0
        return round(min(100.0, (self.current_value / self.target_value) * 100), 1)
    
    @property
    def is_overdue(self) -> bool:
        """Check if goal is overdue"""
        if not self.deadline or self.is_completed:
            return False
        return datetime.now(timezone.utc) > self.deadline.replace(tzinfo=timezone.utc)
    
    def to_dict(self):
        """Convert goal to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "unit": self.unit,
            "is_completed": self.is_completed,
            "is_active": self.is_active,
            "progress_percentage": self.progress_percentage,
            "is_overdue": self.is_overdue,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class GoalProgress(Base):
    __tablename__ = "goal_progress"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Progress Information
    value = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    goal = relationship("Goal", back_populates="goal_progress")
    user = relationship("User", back_populates="goal_progress")
    
    def __repr__(self):
        return f"<GoalProgress(id={self.id}, goal_id={self.goal_id}, value={self.value})>"
