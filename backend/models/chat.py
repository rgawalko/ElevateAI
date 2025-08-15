from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, BigInteger, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime, timezone


class Chat(Base):
    """
    Chat model representing a conversation session between a user and the AI assistant.
    Each chat can contain multiple messages.
    """
    __tablename__ = "chats"

    # Primary Key
    chat_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Chat Information
    title = Column(String(255), nullable=True)  # Optional chat title (can be auto-generated from first message)
    azure_thread_id = Column(String(255), nullable=True, unique=True, index=True)  # Azure OpenAI thread ID
    
    # Chat Status
    is_active = Column(Boolean, default=True)  # Whether the chat is active or archived
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_message_at = Column(DateTime, nullable=True)  # Timestamp of the last message in this chat
    
    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.sent_at")
    
    def __repr__(self):
        return f"<Chat(chat_id={self.chat_id}, user_id={self.user_id}, title={self.title})>"
    
    def to_dict(self):
        """Convert chat object to dictionary"""
        return {
            "chat_id": self.chat_id,
            "user_id": str(self.user_id),
            "title": self.title,
            "azure_thread_id": self.azure_thread_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "message_count": len(self.messages) if self.messages else 0
        }


class Message(Base):
    """
    Message model representing individual messages within a chat conversation.
    Can be from user or AI assistant.
    """
    __tablename__ = "messages"

    # Primary Key
    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    chat_id = Column(BigInteger, ForeignKey("chats.chat_id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for AI messages
    
    # Message Content
    content = Column(Text, nullable=False)  # The actual message content
    message_type = Column(String(50), default='text', nullable=False)  # 'text', 'system', 'error', etc.
    sender_type = Column(String(20), default='user', nullable=False)  # 'user' or 'assistant'
    
    # Message Metadata
    azure_message_id = Column(String(255), nullable=True)  # Azure OpenAI message ID if applicable
    token_count = Column(BigInteger, nullable=True)  # Token count for AI messages (for usage tracking)
    
    # Timestamps
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])  # User who sent the message (null for AI)
    
    def __repr__(self):
        return f"<Message(message_id={self.message_id}, chat_id={self.chat_id}, sender_type={self.sender_type})>"
    
    def to_dict(self):
        """Convert message object to dictionary"""
        return {
            "message_id": self.message_id,
            "chat_id": self.chat_id,
            "sender_id": str(self.sender_id) if self.sender_id else None,
            "content": self.content,
            "message_type": self.message_type,
            "sender_type": self.sender_type,
            "azure_message_id": self.azure_message_id,
            "token_count": self.token_count,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None
        }


# Create indexes for optimal query performance
Index('idx_chats_user_updated', Chat.user_id, Chat.updated_at.desc())
Index('idx_chats_user_active', Chat.user_id, Chat.is_active)
Index('idx_messages_chat_sent', Message.chat_id, Message.sent_at.desc())
Index('idx_messages_sender_type', Message.sender_type)
Index('idx_messages_chat_sender_sent', Message.chat_id, Message.sender_type, Message.sent_at.desc())
