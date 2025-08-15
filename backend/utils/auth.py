"""
Authentication utilities for Elevate AI backend
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with salt.
    In production, consider using bcrypt or argon2 for better security.
    """
    # Generate a random salt
    salt = secrets.token_hex(16)
    
    # Hash the password with salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Return salt + hash (salt is first 32 characters)
    return salt + password_hash


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    """
    if len(hashed_password) < 32:
        return False
    
    # Extract salt (first 32 characters) and hash
    salt = hashed_password[:32]
    stored_hash = hashed_password[32:]
    
    # Hash the provided password with the stored salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Compare hashes
    return password_hash == stored_hash


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verify and decode a JWT token.
    Returns the payload if valid, None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return None
        
        return payload
    except jwt.PyJWTError:
        return None


def generate_verification_token() -> str:
    """
    Generate a random verification token for email verification.
    """
    return secrets.token_urlsafe(32)


def generate_reset_token(user_id: str) -> str:
    """
    Generate a password reset token.
    """
    data = {
        "user_id": user_id,
        "purpose": "password_reset"
    }
    expire = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
    data.update({"exp": expire})
    
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return user_id if valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check purpose
        if payload.get("purpose") != "password_reset":
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return None
        
        return payload.get("user_id")
    except jwt.PyJWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from a valid access token.
    """
    payload = verify_token(token, "access")
    if payload:
        return payload.get("sub")  # 'sub' is the standard JWT claim for subject (user ID)
    return None


def create_token_pair(user_id: str, email: str) -> dict:
    """
    Create both access and refresh tokens for a user.
    """
    access_token_data = {"sub": user_id, "email": email}
    refresh_token_data = {"sub": user_id}
    
    access_token = create_access_token(access_token_data)
    refresh_token = create_refresh_token(refresh_token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    }


def refresh_access_token(refresh_token: str) -> Optional[dict]:
    """
    Create a new access token using a valid refresh token.
    """
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Create new access token (you might want to fetch user email from database)
    access_token_data = {"sub": user_id}
    access_token = create_access_token(access_token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


# Password strength validation
def validate_password_strength(password: str) -> dict:
    """
    Validate password strength and return feedback.
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "strength": "strong" if len(errors) == 0 else "weak"
    }
