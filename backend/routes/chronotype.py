"""
Chronotype quiz API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from database.database import get_db
from utils.auth import verify_token
from services import ChronotypeService
from schemas.chronotype import (
    ChronotypeQuizSubmission,
    ChronotypeQuizResponse,
    ChronotypeResult,
    ChronotypeQuizStructure
)

router = APIRouter(prefix="/chronotype", tags=["chronotype"])
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to get current authenticated user ID
    """
    token = credentials.credentials
    payload = verify_token(token, "access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


@router.get("/quiz", response_model=Dict[str, Any])
async def get_quiz_structure():
    """
    Get the chronotype quiz structure with all questions
    """
    try:
        chronotype_service = ChronotypeService(None)  # No DB needed for static data
        quiz_data = chronotype_service.get_quiz_structure()
        
        return {
            "success": True,
            "data": quiz_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving quiz structure: {str(e)}"
        )


@router.post("/submit", response_model=ChronotypeQuizResponse)
async def submit_quiz(
    submission: ChronotypeQuizSubmission,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Submit chronotype quiz answers and get results
    """
    try:
        chronotype_service = ChronotypeService(db)
        
        # Check if user has already completed the quiz
        if chronotype_service.has_completed_quiz(current_user_id):
            return ChronotypeQuizResponse(
                success=False,
                message="You have already completed the chronotype quiz. Use the update endpoint to retake it."
            )
        
        # Process the quiz submission
        result = chronotype_service.process_quiz_submission(current_user_id, submission)
        
        if result:
            return ChronotypeQuizResponse(
                success=True,
                result=result,
                message="Chronotype quiz completed successfully!"
            )
        else:
            return ChronotypeQuizResponse(
                success=False,
                message="Failed to process quiz submission. Please try again."
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing quiz submission: {str(e)}"
        )


@router.put("/update", response_model=ChronotypeQuizResponse)
async def update_quiz_result(
    submission: ChronotypeQuizSubmission,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update/retake chronotype quiz (overwrites previous results)
    """
    try:
        chronotype_service = ChronotypeService(db)
        
        # Process the quiz submission (this will overwrite existing data)
        result = chronotype_service.process_quiz_submission(current_user_id, submission)
        
        if result:
            return ChronotypeQuizResponse(
                success=True,
                result=result,
                message="Chronotype quiz updated successfully!"
            )
        else:
            return ChronotypeQuizResponse(
                success=False,
                message="Failed to update quiz results. Please try again."
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating quiz results: {str(e)}"
        )


@router.get("/result", response_model=Dict[str, Any])
async def get_chronotype_result(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get user's chronotype result if available
    """
    try:
        chronotype_service = ChronotypeService(db)
        
        result = chronotype_service.get_user_chronotype(current_user_id)
        
        if result:
            return {
                "success": True,
                "data": result,
                "has_completed": True
            }
        else:
            return {
                "success": True,
                "data": None,
                "has_completed": False,
                "message": "Chronotype quiz not completed yet"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chronotype result: {str(e)}"
        )


@router.get("/status", response_model=Dict[str, Any])
async def get_quiz_status(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Check if user has completed the chronotype quiz
    """
    try:
        chronotype_service = ChronotypeService(db)
        
        has_completed = chronotype_service.has_completed_quiz(current_user_id)
        
        return {
            "success": True,
            "has_completed": has_completed,
            "message": "Quiz completed" if has_completed else "Quiz not completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking quiz status: {str(e)}"
        )


@router.get("/statistics", response_model=Dict[str, Any])
async def get_chronotype_statistics(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get chronotype distribution statistics (admin/analytics endpoint)
    """
    try:
        chronotype_service = ChronotypeService(db)
        
        stats = chronotype_service.get_chronotype_statistics()
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chronotype statistics: {str(e)}"
        )


@router.delete("/result")
async def delete_chronotype_result(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete user's chronotype result (allows retaking the quiz)
    """
    try:
        chronotype_service = ChronotypeService(db)
        
        # Get user and clear chronotype data
        from models.user import User
        user = db.query(User).filter(User.id == current_user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.chronotype_data is None:
            return {
                "success": True,
                "message": "No chronotype data to delete"
            }
        
        user.chronotype_data = None
        db.commit()
        
        return {
            "success": True,
            "message": "Chronotype data deleted successfully. You can now retake the quiz."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting chronotype result: {str(e)}"
        )
