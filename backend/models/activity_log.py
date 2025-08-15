from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    activities = Column(JSON)  # structured activity data (e.g., task, mood, time)
    notes = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    activity_tags = relationship("ActivityTag", back_populates="activity_log", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ActivityLog(id={self.id}, user_id={self.user_id}, date={self.date})>"

    def to_dict(self):
        """Convert activity log to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat() if self.date else None,
            "activities": self.activities,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }