"""
Chronotype service for processing quiz results and managing chronotype data
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models.user import User
from schemas.chronotype import (
    ChronotypeQuizSubmission, 
    ChronotypeResult, 
    ChronotypeClassification,
    PeakWindow,
    CHRONOTYPE_QUIZ_DATA
)
from services.base_service import BaseService


class ChronotypeService(BaseService):
    """Service for handling chronotype quiz and results"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.model = User

    def calculate_chronotype(self, answers: List[int]) -> ChronotypeResult:
        """
        Calculate chronotype based on quiz answers
        
        Args:
            answers: List of 9 answers, each scored 1-5
            
        Returns:
            ChronotypeResult with classification and recommendations
        """
        # Validate answers
        if len(answers) != 9:
            raise ValueError("Quiz must have exactly 9 answers")
        
        if not all(1 <= answer <= 5 for answer in answers):
            raise ValueError("All answers must be between 1 and 5")
        
        # Calculate total score
        total = sum(answers)
        
        # Determine chronotype classification
        if 9 <= total <= 20:
            chronotype = ChronotypeClassification.LARK
            peak_window = PeakWindow(start="07:00", end="11:00")
            secondary_window = PeakWindow(start="13:00", end="15:00")
            description = "You are a morning person (Lark). You naturally wake up early, feel most alert in the morning, and prefer to go to bed early."
            recommendations = [
                "Schedule important tasks between 7:00-11:00 AM",
                "Take advantage of your natural early morning energy",
                "Avoid late-night activities when possible",
                "Maintain consistent early sleep schedule",
                "Use afternoon secondary peak (1:00-3:00 PM) for less demanding tasks"
            ]
        elif 21 <= total <= 30:
            chronotype = ChronotypeClassification.INTERMEDIATE
            peak_window = PeakWindow(start="09:00", end="12:00")
            secondary_window = PeakWindow(start="14:00", end="16:00")
            description = "You are an intermediate type (Hummingbird). You have a flexible sleep-wake cycle and can adapt to different schedules."
            recommendations = [
                "Schedule important tasks between 9:00 AM-12:00 PM",
                "Take advantage of your adaptability for varying schedules",
                "Use afternoon peak (2:00-4:00 PM) for creative work",
                "Maintain consistent sleep routine for optimal performance",
                "You can handle both morning and evening activities reasonably well"
            ]
        elif 31 <= total <= 45:
            chronotype = ChronotypeClassification.OWL
            peak_window = PeakWindow(start="16:00", end="20:00")
            secondary_window = PeakWindow(start="10:00", end="12:00")
            description = "You are an evening person (Owl). You naturally stay up late, feel most alert in the evening, and prefer to wake up later."
            recommendations = [
                "Schedule important tasks between 4:00-8:00 PM",
                "Use late morning secondary peak (10:00 AM-12:00 PM) when needed",
                "Avoid early morning commitments when possible",
                "Embrace your natural late-night productivity",
                "Consider flexible work arrangements if available"
            ]
        else:
            raise ValueError(f"Invalid total score: {total}. Must be between 9 and 45.")
        
        return ChronotypeResult(
            answers=answers,
            total=total,
            chronotype=chronotype,
            peak_window=peak_window,
            secondary_window=secondary_window,
            description=description,
            recommendations=recommendations
        )

    def save_chronotype_result(self, user_id: str, quiz_result: ChronotypeResult) -> bool:
        """
        Save chronotype quiz result to user's profile
        
        Args:
            user_id: User ID
            quiz_result: Calculated chronotype result
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                self.logger.error(f"User not found: {user_id}")
                return False
            
            # Convert result to dictionary for JSON storage
            chronotype_data = {
                "answers": quiz_result.answers,
                "total": quiz_result.total,
                "chronotype": quiz_result.chronotype.value,
                "peak_window": {
                    "start": quiz_result.peak_window.start,
                    "end": quiz_result.peak_window.end
                },
                "secondary_window": {
                    "start": quiz_result.secondary_window.start,
                    "end": quiz_result.secondary_window.end
                },
                "description": quiz_result.description,
                "recommendations": quiz_result.recommendations,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "quiz_version": "1.0"
            }
            
            # Update user's chronotype data
            user.chronotype_data = chronotype_data
            user.updated_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.logger.info(f"Saved chronotype result for user {user_id}: {quiz_result.chronotype.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving chronotype result for user {user_id}: {e}")
            self.db.rollback()
            return False

    def get_user_chronotype(self, user_id: str) -> Optional[ChronotypeResult]:
        """
        Get user's chronotype result if available
        
        Args:
            user_id: User ID
            
        Returns:
            ChronotypeResult if available, None otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.chronotype_data:
                return None
            
            data = user.chronotype_data
            
            # Convert stored data back to ChronotypeResult
            return ChronotypeResult(
                answers=data["answers"],
                total=data["total"],
                chronotype=ChronotypeClassification(data["chronotype"]),
                peak_window=PeakWindow(
                    start=data["peak_window"]["start"],
                    end=data["peak_window"]["end"]
                ),
                secondary_window=PeakWindow(
                    start=data["secondary_window"]["start"],
                    end=data["secondary_window"]["end"]
                ),
                description=data.get("description"),
                recommendations=data.get("recommendations", [])
            )
            
        except Exception as e:
            self.logger.error(f"Error retrieving chronotype for user {user_id}: {e}")
            return None

    def has_completed_quiz(self, user_id: str) -> bool:
        """
        Check if user has completed the chronotype quiz
        
        Args:
            user_id: User ID
            
        Returns:
            True if quiz completed, False otherwise
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            return user is not None and user.chronotype_data is not None
        except Exception as e:
            self.logger.error(f"Error checking quiz completion for user {user_id}: {e}")
            return False

    def get_quiz_structure(self) -> Dict[str, Any]:
        """
        Get the complete quiz structure for frontend
        
        Returns:
            Dictionary containing quiz questions and structure
        """
        return CHRONOTYPE_QUIZ_DATA

    def process_quiz_submission(self, user_id: str, submission: ChronotypeQuizSubmission) -> Optional[ChronotypeResult]:
        """
        Process a complete quiz submission
        
        Args:
            user_id: User ID
            submission: Quiz submission with answers
            
        Returns:
            ChronotypeResult if successful, None otherwise
        """
        try:
            # Validate submission
            if not submission.validate_answers():
                self.logger.error(f"Invalid quiz answers for user {user_id}")
                return None
            
            # Calculate chronotype
            result = self.calculate_chronotype(submission.answers)
            
            # Save to database
            if self.save_chronotype_result(user_id, result):
                return result
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing quiz submission for user {user_id}: {e}")
            return None

    def get_chronotype_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about chronotype distribution
        
        Returns:
            Dictionary with chronotype statistics
        """
        try:
            # Get all users with chronotype data
            users_with_chronotype = self.db.query(User).filter(
                User.chronotype_data.isnot(None)
            ).all()
            
            total_completed = len(users_with_chronotype)
            
            if total_completed == 0:
                return {
                    "total_completed": 0,
                    "distribution": {},
                    "percentages": {}
                }
            
            # Count chronotypes
            chronotype_counts = {
                "Lark": 0,
                "Intermediate": 0,
                "Owl": 0
            }
            
            for user in users_with_chronotype:
                chronotype = user.chronotype_data.get("chronotype")
                if chronotype in chronotype_counts:
                    chronotype_counts[chronotype] += 1
            
            # Calculate percentages
            percentages = {
                chronotype: (count / total_completed * 100)
                for chronotype, count in chronotype_counts.items()
            }
            
            return {
                "total_completed": total_completed,
                "distribution": chronotype_counts,
                "percentages": percentages
            }
            
        except Exception as e:
            self.logger.error(f"Error getting chronotype statistics: {e}")
            return {
                "total_completed": 0,
                "distribution": {},
                "percentages": {}
            }
