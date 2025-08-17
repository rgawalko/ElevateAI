"""
Authentication routes for Elevate AI
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from database.utils import get_db
from schemas.user import UserCreate, UserLogin, UserOut
from services import UserService, RegisterService
from models import User
from utils.auth import create_token_pair, verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account with comprehensive validation
    """
    register_service = RegisterService(db)

    # Validate registration data
    validation = register_service.validate_registration_data(user_data)
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["errors"][0] if validation["errors"] else "Registration validation failed"
        )

    # Create user account
    db_user = register_service.create_user_account(user_data)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user account. Please try again."
        )

    # Create tokens
    tokens = create_token_pair(str(db_user.id), db_user.email)

    response_data = {
        "message": "User registered successfully",
        "user": UserOut.model_validate(db_user),
        "tokens": tokens
    }

    # Add warnings if any
    if validation.get("warnings"):
        response_data["warnings"] = validation["warnings"]

    return response_data


@router.post("/validate-password", response_model=Dict[str, Any])
async def validate_password(password_data: Dict[str, str], db: Session = Depends(get_db)):
    """
    Validate password strength for real-time feedback
    """
    password = password_data.get("password", "")
    register_service = RegisterService(db)

    validation = register_service.validate_password_strength(password)

    return {
        "is_valid": validation["is_valid"],
        "strength": validation["strength"],
        "errors": validation["errors"]
    }


@router.post("/check-email", response_model=Dict[str, Any])
async def check_email_availability(email_data: Dict[str, str], db: Session = Depends(get_db)):
    """
    Check if email is available for registration
    """
    email = email_data.get("email", "")
    register_service = RegisterService(db)

    is_available = register_service.check_email_availability(email)
    is_valid_format = register_service.validate_email_format(email)

    return {
        "available": is_available,
        "valid_format": is_valid_format,
        "message": "Email is available" if is_available and is_valid_format else
                  "Invalid email format" if not is_valid_format else "Email already registered"
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
