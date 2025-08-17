import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session

from services.azure_chatbot_service import AzureChatbotService
from services.chat_service import ChatService
from services.user_service import UserService
# ChatbotTools class removed - functions are now standalone
from database.database import get_db
from models import Chat, Message, User
from utils.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])
security = HTTPBearer()
# Updated to use JWT authentication instead of user_id in request body

# Helper function to get authenticated user
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract user ID from JWT token
    """
    token = credentials.credentials

    # Verify access token
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    return user_id

# Initialize the Azure chatbot service
try:
    chatbot_service = AzureChatbotService()
    logger.info("✅ Chatbot service initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize chatbot service: {e}")
    chatbot_service = None

# Pydantic models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User message to send to the chatbot")
    chat_id: Optional[int] = Field(None, description="Optional chat ID for continuing conversation")

class ChatResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    chat_id: int
    message_id: int
    timestamp: Optional[str] = None
    error: Optional[str] = None

class ConversationHistoryResponse(BaseModel):
    success: bool
    messages: List[Dict[str, Any]] = []
    chat_id: int
    total_messages: int
    error: Optional[str] = None

class ChatListResponse(BaseModel):
    success: bool
    chats: List[Dict[str, Any]] = []
    total_chats: int
    error: Optional[str] = None

class CreateChatRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Optional chat title")

class CreateChatResponse(BaseModel):
    success: bool
    chat_id: Optional[int] = None
    error: Optional[str] = None

# Demo user creation function removed - using real authenticated users

@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatMessage,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Send a message to the AI chatbot

    Args:
        chat_request: Contains the message and optional chat_id
        db: Database session
        user_id: Authenticated user ID from JWT token

    Returns:
        ChatResponse with the AI's reply and conversation metadata
    """
    try:
        if not chatbot_service:
            raise HTTPException(
                status_code=503,
                detail="Chatbot service is not available"
            )

        logger.info(f"💬 Received chat message from user {user_id}: {chat_request.message[:100]}...")

        chat_svc = ChatService(db)

        # Get or create chat
        chat = None
        if chat_request.chat_id:
            chat = chat_svc.get_chat_by_id(chat_request.chat_id, user_id)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found or access denied")

        # Create new chat if none exists
        if not chat:
            # Create Azure thread first
            azure_thread_id = chatbot_service.create_thread()
            logger.info(f"📝 Created new Azure thread: {azure_thread_id}")

            # Create chat in database
            chat = chat_svc.create_chat(
                user_id=user_id,
                azure_thread_id=azure_thread_id
            )
            logger.info(f"📝 Created new chat: {chat.chat_id}")

        # Add user message to database
        user_message = chat_svc.add_message(
            chat_id=chat.chat_id,
            content=chat_request.message,
            sender_type='user',
            sender_id=user_id
        )

        # Determine which agent to use based on message content
        if chatbot_service.should_use_eps_agent(chat_request.message):
            # Use EPS insights agent for productivity-related queries
            result = chatbot_service.send_message_with_eps_insights(
                thread_id=chat.azure_thread_id,
                message=chat_request.message,
                db_session=db,
                user_id=user_id,
                max_wait_seconds=30
            )
        else:
            # Use regular chatbot for general queries
            result = chatbot_service.send_message_with_functions_official(
                thread_id=chat.azure_thread_id,
                message=chat_request.message,
                db_session=db,
                user_id=user_id,
                max_wait_seconds=30
            )

        if result["success"]:
            # Add AI response to database
            ai_message = chat_svc.add_message(
                chat_id=chat.chat_id,
                content=result["message"],
                sender_type='assistant',
                azure_message_id=result.get("azure_message_id")
            )

            logger.info(f"✅ Successfully processed chat message")
            return ChatResponse(
                success=True,
                message=result["message"],
                chat_id=chat.chat_id,
                message_id=ai_message.message_id,
                timestamp=result.get("timestamp")
            )
        else:
            logger.error(f"❌ Chat processing failed: {result.get('error')}")
            return ChatResponse(
                success=False,
                chat_id=chat.chat_id,
                message_id=user_message.message_id,
                error=result.get("error", "Unknown error occurred")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in send_message endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )

@router.post("/chat/new", response_model=CreateChatResponse)
async def create_new_chat(
    request: CreateChatRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new chat conversation

    Args:
        request: Contains optional title
        db: Database session
        user_id: Authenticated user ID from JWT token

    Returns:
        CreateChatResponse with the new chat ID
    """
    try:
        if not chatbot_service:
            raise HTTPException(
                status_code=503,
                detail="Chatbot service is not available"
            )

        chat_svc = ChatService(db)

        # Create Azure thread first
        azure_thread_id = chatbot_service.create_thread()
        logger.info(f"📝 Created new Azure thread: {azure_thread_id}")

        # Create chat in database
        chat = chat_svc.create_chat(
            user_id=user_id,
            title=request.title,
            azure_thread_id=azure_thread_id
        )

        logger.info(f"📝 Created new chat: {chat.chat_id}")

        return CreateChatResponse(
            success=True,
            chat_id=chat.chat_id
        )

    except Exception as e:
        logger.error(f"❌ Error creating new chat: {e}")
        return CreateChatResponse(
            success=False,
            error=f"Failed to create new chat: {str(e)}"
        )

@router.get("/chat/{chat_id}/messages", response_model=ConversationHistoryResponse)
async def get_chat_messages(
    chat_id: int,
    limit: int = 50,
    before_timestamp: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get messages from a specific chat

    Args:
        chat_id: The chat ID
        limit: Maximum number of messages to retrieve (default: 50)
        before_timestamp: Get messages before this timestamp (for pagination)
        db: Database session
        user_id: Authenticated user ID from JWT token

    Returns:
        ConversationHistoryResponse with message history
    """
    try:
        chat_svc = ChatService(db)

        # Parse timestamp if provided
        before_dt = None
        if before_timestamp:
            try:
                before_dt = datetime.fromisoformat(before_timestamp.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid timestamp format")

        logger.info(f"📚 Retrieving messages for chat {chat_id}, user {user_id}")

        messages = chat_svc.get_chat_messages(
            chat_id=chat_id,
            user_id=user_id,
            limit=min(limit, 100),  # Cap at 100 messages
            before_timestamp=before_dt
        )

        # Convert messages to dict format
        message_dicts = [msg.to_dict() for msg in messages]

        return ConversationHistoryResponse(
            success=True,
            messages=message_dicts,
            chat_id=chat_id,
            total_messages=len(message_dicts)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving chat messages: {e}")
        return ConversationHistoryResponse(
            success=False,
            chat_id=chat_id,
            total_messages=0,
            error=f"Failed to retrieve chat messages: {str(e)}"
        )

@router.get("/chats", response_model=ChatListResponse)
async def get_user_chats(
    limit: int = 50,
    offset: int = 0,
    active_only: bool = True,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all chats for a user

    Args:
        limit: Maximum number of chats to return (default: 50)
        offset: Number of chats to skip (default: 0)
        active_only: Whether to return only active chats (default: True)
        db: Database session
        user_id: Authenticated user ID from JWT token

    Returns:
        ChatListResponse with user's chats
    """
    try:
        chat_svc = ChatService(db)

        logger.info(f"📚 Retrieving chats for user {user_id}")

        chats = chat_svc.get_user_chats(
            user_id=user_id,
            limit=min(limit, 100),  # Cap at 100 chats
            offset=offset,
            active_only=active_only
        )

        # Convert chats to dict format
        chat_dicts = [chat.to_dict() for chat in chats]

        return ChatListResponse(
            success=True,
            chats=chat_dicts,
            total_chats=len(chat_dicts)
        )

    except Exception as e:
        logger.error(f"❌ Error retrieving user chats: {e}")
        return ChatListResponse(
            success=False,
            total_chats=0,
            error=f"Failed to retrieve user chats: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Check if the chatbot service is healthy and available

    Returns:
        Health status information
    """
    try:
        if not chatbot_service:
            return {
                "status": "unhealthy",
                "message": "Chatbot service is not initialized",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # Try to get agent info to verify connection
        _ = chatbot_service.agent  # Just verify we can access the agent

        return {
            "status": "healthy",
            "message": "Chatbot service is operational",
            "agent_id": chatbot_service.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
