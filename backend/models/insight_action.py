from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone


class InsightAction(Base):
    __tablename__ = "insight_actions"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    insight_id = Column(UUID(as_uuid=True), ForeignKey("ai_insights.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Action Information
    action_type = Column(String(50), nullable=False)  # viewed, dismissed, implemented, etc.
    action_data = Column(Text, nullable=True)  # Additional action-specific data
    notes = Column(Text, nullable=True)  # User notes about the action
    
    # Status
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    insight = relationship("AIInsight", back_populates="insight_actions")
    user = relationship("User", back_populates="insight_actions")
    
    def __repr__(self):
        return f"<InsightAction(id={self.id}, type={self.action_type}, insight_id={self.insight_id})>"
    
    def to_dict(self):
        """Convert insight action to dictionary"""
        return {
            "id": str(self.id),
            "insight_id": str(self.insight_id),
            "user_id": str(self.user_id),
            "action_type": self.action_type,
            "action_data": self.action_data,
            "notes": self.notes,
            "is_completed": self.is_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
