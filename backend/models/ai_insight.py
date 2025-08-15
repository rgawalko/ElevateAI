from sqlalchemy import Column, DateTime, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone

class AIInsight(Base):
    __tablename__ = "ai_insights"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    insight_type = Column(String)
    summary = Column(String)
    suggestions = Column(JSON)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="ai_insights")
    insight_actions = relationship("InsightAction", back_populates="insight", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AIInsight(id={self.id}, type={self.insight_type}, user_id={self.user_id})>"

    def to_dict(self):
        """Convert AI insight to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "date": self.date.isoformat() if self.date else None,
            "insight_type": self.insight_type,
            "summary": self.summary,
            "suggestions": self.suggestions,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }
