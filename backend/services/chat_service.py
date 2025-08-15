import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from models import Chat, Message, User
from database.database import get_db

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations and messages"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_chat(self, user_id: str, title: Optional[str] = None, azure_thread_id: Optional[str] = None) -> Chat:
        """
        Create a new chat conversation
        
        Args:
            user_id: UUID of the user creating the chat
            title: Optional title for the chat
            azure_thread_id: Optional Azure OpenAI thread ID
            
        Returns:
            Chat: The created chat object
        """
        try:
            chat = Chat(
                user_id=user_id,
                title=title,
                azure_thread_id=azure_thread_id
            )
            
            self.db.add(chat)
            self.db.commit()
            self.db.refresh(chat)
            
            logger.info(f"Created new chat {chat.chat_id} for user {user_id}")
            return chat
            
        except Exception as e:
            logger.error(f"Error creating chat for user {user_id}: {e}")
            self.db.rollback()
            raise
    
    def get_chat_by_id(self, chat_id: int, user_id: str) -> Optional[Chat]:
        """
        Get a chat by ID, ensuring it belongs to the user
        
        Args:
            chat_id: The chat ID
            user_id: The user ID to verify ownership
            
        Returns:
            Chat or None if not found or not owned by user
        """
        try:
            chat = self.db.query(Chat).filter(
                and_(Chat.chat_id == chat_id, Chat.user_id == user_id)
            ).first()
            
            return chat
            
        except Exception as e:
            logger.error(f"Error getting chat {chat_id} for user {user_id}: {e}")
            return None
    
    def get_chat_by_azure_thread(self, azure_thread_id: str, user_id: str) -> Optional[Chat]:
        """
        Get a chat by Azure thread ID
        
        Args:
            azure_thread_id: The Azure OpenAI thread ID
            user_id: The user ID to verify ownership
            
        Returns:
            Chat or None if not found
        """
        try:
            chat = self.db.query(Chat).filter(
                and_(Chat.azure_thread_id == azure_thread_id, Chat.user_id == user_id)
            ).first()
            
            return chat
            
        except Exception as e:
            logger.error(f"Error getting chat by Azure thread {azure_thread_id} for user {user_id}: {e}")
            return None
    
    def get_user_chats(self, user_id: str, limit: int = 50, offset: int = 0, active_only: bool = True) -> List[Chat]:
        """
        Get all chats for a user with pagination
        
        Args:
            user_id: The user ID
            limit: Maximum number of chats to return
            offset: Number of chats to skip
            active_only: Whether to return only active chats
            
        Returns:
            List of Chat objects
        """
        try:
            query = self.db.query(Chat).filter(Chat.user_id == user_id)
            
            if active_only:
                query = query.filter(Chat.is_active == True)
            
            chats = query.order_by(desc(Chat.updated_at)).limit(limit).offset(offset).all()
            
            logger.info(f"Retrieved {len(chats)} chats for user {user_id}")
            return chats
            
        except Exception as e:
            logger.error(f"Error getting chats for user {user_id}: {e}")
            return []
    
    def add_message(self, chat_id: int, content: str, sender_type: str = 'user', 
                   sender_id: Optional[str] = None, message_type: str = 'text',
                   azure_message_id: Optional[str] = None, token_count: Optional[int] = None) -> Message:
        """
        Add a message to a chat
        
        Args:
            chat_id: The chat ID
            content: The message content
            sender_type: 'user' or 'assistant'
            sender_id: User ID if sender_type is 'user', None for assistant
            message_type: Type of message ('text', 'system', 'error', etc.)
            azure_message_id: Azure OpenAI message ID if applicable
            token_count: Token count for AI messages
            
        Returns:
            Message: The created message object
        """
        try:
            message = Message(
                chat_id=chat_id,
                content=content,
                sender_type=sender_type,
                sender_id=sender_id,
                message_type=message_type,
                azure_message_id=azure_message_id,
                token_count=token_count
            )
            
            self.db.add(message)
            
            # Update chat's last_message_at timestamp
            chat = self.db.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                chat.last_message_at = datetime.now(timezone.utc)
                chat.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Added {sender_type} message to chat {chat_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error adding message to chat {chat_id}: {e}")
            self.db.rollback()
            raise
    
    def get_chat_messages(self, chat_id: int, user_id: str, limit: int = 50, 
                         before_timestamp: Optional[datetime] = None) -> List[Message]:
        """
        Get messages from a chat with pagination
        
        Args:
            chat_id: The chat ID
            user_id: User ID to verify chat ownership
            limit: Maximum number of messages to return
            before_timestamp: Get messages before this timestamp (for pagination)
            
        Returns:
            List of Message objects ordered by sent_at DESC
        """
        try:
            # First verify the user owns this chat
            chat = self.get_chat_by_id(chat_id, user_id)
            if not chat:
                logger.warning(f"User {user_id} attempted to access chat {chat_id} they don't own")
                return []
            
            query = self.db.query(Message).filter(Message.chat_id == chat_id)
            
            if before_timestamp:
                query = query.filter(Message.sent_at < before_timestamp)
            
            messages = query.order_by(desc(Message.sent_at)).limit(limit).all()
            
            logger.info(f"Retrieved {len(messages)} messages from chat {chat_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages from chat {chat_id}: {e}")
            return []
    
    def update_chat_title(self, chat_id: int, user_id: str, title: str) -> bool:
        """
        Update a chat's title
        
        Args:
            chat_id: The chat ID
            user_id: User ID to verify ownership
            title: New title for the chat
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            chat = self.get_chat_by_id(chat_id, user_id)
            if not chat:
                return False
            
            chat.title = title
            chat.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            logger.info(f"Updated title for chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating chat {chat_id} title: {e}")
            self.db.rollback()
            return False
    
    def archive_chat(self, chat_id: int, user_id: str) -> bool:
        """
        Archive a chat (set is_active to False)
        
        Args:
            chat_id: The chat ID
            user_id: User ID to verify ownership
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            chat = self.get_chat_by_id(chat_id, user_id)
            if not chat:
                return False
            
            chat.is_active = False
            chat.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            
            logger.info(f"Archived chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error archiving chat {chat_id}: {e}")
            self.db.rollback()
            return False
    
    def delete_chat(self, chat_id: int, user_id: str) -> bool:
        """
        Permanently delete a chat and all its messages
        
        Args:
            chat_id: The chat ID
            user_id: User ID to verify ownership
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            chat = self.get_chat_by_id(chat_id, user_id)
            if not chat:
                return False
            
            self.db.delete(chat)  # Cascade will delete all messages
            self.db.commit()
            
            logger.info(f"Deleted chat {chat_id} and all its messages")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            self.db.rollback()
            return False
