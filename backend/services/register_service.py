"""
Registration service for Elevate AI backend
Handles user registration logic and validation
"""

import re
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from models.user import User
from schemas.user import UserCreate
from utils.auth import hash_password
from services.base_service import BaseService


class RegisterService(BaseService):
    """Service for handling user registration"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.model = User

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Validate password strength and return detailed feedback
        
        Args:
            password: The password to validate
            
        Returns:
            Dict containing validation results and feedback
        """
        errors = []
        
        # Check minimum length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digit
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        # Check for special character (optional but recommended)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            # This is a warning, not an error
            pass
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength": self._calculate_password_strength(password)
        }

    def _calculate_password_strength(self, password: str) -> str:
        """Calculate password strength score"""
        score = 0
        
        # Length bonus
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # Character variety
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        
        # Return strength level
        if score <= 2:
            return "weak"
        elif score <= 4:
            return "medium"
        else:
            return "strong"

    def validate_email_format(self, email: str) -> bool:
        """
        Validate email format using regex
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email format is valid, False otherwise
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

    def check_email_availability(self, email: str) -> bool:
        """
        Check if email is available for registration
        
        Args:
            email: Email address to check
            
        Returns:
            True if email is available, False if already taken
        """
        try:
            existing_user = self.db.query(User).filter(User.email == email).first()
            return existing_user is None
        except Exception as e:
            self.logger.error(f"Error checking email availability: {e}")
            return False

    def validate_registration_data(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Comprehensive validation of registration data
        
        Args:
            user_data: User registration data
            
        Returns:
            Dict containing validation results
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }

        # Validate name
        if not user_data.name or len(user_data.name.strip()) < 1:
            validation_result["errors"].append("Name is required")
            validation_result["is_valid"] = False
        elif len(user_data.name) > 255:
            validation_result["errors"].append("Name must be less than 255 characters")
            validation_result["is_valid"] = False

        # Validate email format
        if not self.validate_email_format(user_data.email):
            validation_result["errors"].append("Invalid email format")
            validation_result["is_valid"] = False

        # Check email availability
        if not self.check_email_availability(user_data.email):
            validation_result["errors"].append("Email address is already registered")
            validation_result["is_valid"] = False

        # Validate password strength
        password_validation = self.validate_password_strength(user_data.password)
        if not password_validation["is_valid"]:
            validation_result["errors"].extend(password_validation["errors"])
            validation_result["is_valid"] = False
        elif password_validation["strength"] == "weak":
            validation_result["warnings"].append("Consider using a stronger password")

        # Validate timezone (optional)
        if user_data.timezone:
            try:
                # Basic timezone validation - you might want to use pytz for more comprehensive validation
                import zoneinfo
                zoneinfo.ZoneInfo(user_data.timezone)
            except Exception:
                validation_result["warnings"].append("Invalid timezone, defaulting to UTC")

        return validation_result

    def create_user_account(self, user_data: UserCreate) -> Optional[User]:
        """
        Create a new user account with validation
        
        Args:
            user_data: User registration data
            
        Returns:
            Created User object if successful, None if failed
        """
        try:
            # Validate registration data
            validation = self.validate_registration_data(user_data)
            if not validation["is_valid"]:
                self.logger.warning(f"Registration validation failed: {validation['errors']}")
                return None

            # Hash the password
            password_hash = hash_password(user_data.password)

            # Create user object
            db_user = User(
                name=user_data.name.strip(),
                email=user_data.email.lower().strip(),
                password_hash=password_hash,
                avatar=user_data.avatar,
                bio=user_data.bio,
                timezone=user_data.timezone or "UTC",
                date_format=user_data.date_format or "YYYY-MM-DD",
                time_format=user_data.time_format or "24h",
                is_active=True,
                is_verified=False,  # Email verification can be implemented later
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )

            # Save to database
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)

            self.logger.info(f"Successfully created user account: {user_data.email}")
            return db_user

        except Exception as e:
            self.logger.error(f"Error creating user account: {e}")
            self.db.rollback()
            return None

    def get_registration_statistics(self) -> Dict[str, Any]:
        """
        Get registration statistics for admin purposes
        
        Returns:
            Dict containing registration stats
        """
        try:
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            verified_users = self.db.query(User).filter(User.is_verified == True).count()
            
            # Recent registrations (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_registrations = self.db.query(User).filter(
                User.created_at >= thirty_days_ago
            ).count()

            return {
                "total_users": total_users,
                "active_users": active_users,
                "verified_users": verified_users,
                "recent_registrations": recent_registrations,
                "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
            }

        except Exception as e:
            self.logger.error(f"Error getting registration statistics: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "verified_users": 0,
                "recent_registrations": 0,
                "verification_rate": 0
            }
