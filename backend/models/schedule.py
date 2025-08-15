from sqlalchemy import Column, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date = Column(DateTime)
    tasks = Column(JSON)
    generated_by_ai = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="schedules")
    schedule_tasks = relationship("ScheduleTask", back_populates="schedule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Schedule(id={self.id}, user_id={self.user_id}, date={self.date}, ai_generated={self.generated_by_ai})>"

    def to_dict(self):
        """Convert schedule to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat() if self.date else None,
            "tasks": self.tasks,
            "generated_by_ai": self.generated_by_ai,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
