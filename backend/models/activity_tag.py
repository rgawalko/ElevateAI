from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone


class ActivityTag(Base):
    __tablename__ = "activity_tags"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    activity_log_id = Column(UUID(as_uuid=True), ForeignKey("activity_logs.id"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    activity_log = relationship("ActivityLog", back_populates="activity_tags")
    tag = relationship("Tag", back_populates="activity_tags")
    
    # Ensure unique activity-tag combinations
    __table_args__ = (UniqueConstraint('activity_log_id', 'tag_id', name='unique_activity_tag'),)
    
    def __repr__(self):
        return f"<ActivityTag(activity_log_id={self.activity_log_id}, tag_id={self.tag_id})>"


class Tag(Base):
    __tablename__ = "tags"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Tag Information
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=True)  # Hex color code like #FF5733
    description = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="tags")
    activity_tags = relationship("ActivityTag", back_populates="tag", cascade="all, delete-orphan")
    
    # Ensure unique tag names per user
    __table_args__ = (UniqueConstraint('user_id', 'name', name='unique_user_tag_name'),)
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert tag to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "color": self.color,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
