"""
Authentication routes for Elevate AI
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from database.utils import get_db
from schemas.user import UserCreate, UserLogin, UserOut
from services import UserService
from models import User
from utils.auth import create_token_pair, verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account
    """
    user_service = UserService(db)

    # Check if user already exists
    existing_user = user_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user (service handles password validation and hashing)
    db_user = user_service.create_user(user_data.model_dump())
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user. Please check your input."
        )

    # Create tokens
    tokens = create_token_pair(str(db_user.id), db_user.email)

    return {
        "message": "User registered successfully",
        "user": UserOut.model_validate(db_user),
        "tokens": tokens
    }


@router.post("/login", response_model=Dict[str, Any])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access tokens
    """
    user_service = UserService(db)

    # Authenticate user (service handles all validation)
    user = user_service.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create tokens
    tokens = create_token_pair(str(user.id), user.email)

    return {
        "message": "Login successful",
        "user": UserOut.model_validate(user),
        "tokens": tokens
    }


@router.post("/logout")
async def logout(_: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user (client should discard tokens)
    """
    # In a production app, you might want to blacklist the token
    # For now, we just return a success message
    return {"message": "Logout successful"}


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token using refresh token
    """
    token = credentials.credentials
    
    # Verify refresh token
    payload = verify_token(token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # You might want to verify user still exists and is active
    # For now, we'll create a new access token
    from utils.auth import create_access_token
    new_access_token = create_access_token({"sub": user_id})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserOut)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information
    """
    token = credentials.credentials
    
    # Verify access token
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database using service
    user_service = UserService(db)
    user = user_service.get_by_id(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    return UserOut.model_validate(user)


@router.post("/verify-token")
async def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify if an access token is valid
    """
    token = credentials.credentials
    
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
    
    return {
        "valid": True,
        "user_id": payload.get("sub"),
        "expires_at": payload.get("exp")
    }
