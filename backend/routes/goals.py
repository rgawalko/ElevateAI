"""
Goals API routes for managing user goals and progress tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from database.utils import get_db
from services.goal_service import GoalService
from models.goal import Goal, GoalProgress
from utils.auth import verify_token
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/goals", tags=["goals"])
security = HTTPBearer()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to get current authenticated user ID
    """
    token = credentials.credentials
    payload = verify_token(token, "access")

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    return user_id

# Pydantic models for request/response
class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    target_value: float
    unit: str
    deadline: Optional[datetime] = None

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    deadline: Optional[datetime] = None
    is_completed: Optional[bool] = None
    is_active: Optional[bool] = None

class GoalProgressAdd(BaseModel):
    value: float
    notes: Optional[str] = None

@router.get("/")
async def get_user_goals(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
    category: Optional[str] = Query(None, description="Filter by category"),
    active_only: bool = Query(True, description="Show only active goals"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get user's goals with optional filtering and pagination.
    """
    try:
        logger.info(f"Fetching goals for user: {current_user_id}")
        
        goal_service = GoalService(db)
        
        # Build filters
        filters = {}
        if category:
            filters['category'] = category
        if active_only:
            filters['is_active'] = True
        
        # Get goals
        result = goal_service.get_user_goals(
            user_id=current_user_id,
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        # Convert goals to dict format for frontend
        goals_data = []
        for goal in result['items']:
            goal_dict = goal.to_dict()
            goals_data.append(goal_dict)
        
        logger.info(f"Successfully retrieved {len(goals_data)} goals for user: {current_user_id}")
        
        return {
            "success": True,
            "data": {
                "goals": goals_data,
                "pagination": {
                    "total": result['total'],
                    "page": result['page'],
                    "per_page": result['per_page'],
                    "pages": result['pages']
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching goals for user {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch goals")

@router.post("/")
async def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new goal for the user.
    """
    try:
        logger.info(f"Creating goal for user: {current_user_id}")
        
        goal_service = GoalService(db)
        
        # Convert Pydantic model to dict
        goal_dict = goal_data.model_dump()
        
        # Create goal
        goal = goal_service.create_goal(current_user_id, goal_dict)
        
        if not goal:
            raise HTTPException(status_code=400, detail="Failed to create goal")
        
        logger.info(f"Successfully created goal '{goal.title}' for user: {current_user_id}")
        
        return {
            "success": True,
            "data": goal.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating goal for user {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create goal")

@router.get("/{goal_id}")
async def get_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific goal with progress history.
    """
    try:
        goal_service = GoalService(db)
        
        goal = goal_service.get_goal_with_progress(goal_id, current_user_id)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return {
            "success": True,
            "data": goal.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching goal {goal_id} for user {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch goal")

@router.put("/{goal_id}")
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update a goal.
    """
    try:
        goal_service = GoalService(db)
        
        # Convert Pydantic model to dict, excluding None values
        update_dict = {k: v for k, v in goal_data.model_dump().items() if v is not None}
        
        goal = goal_service.update_goal(goal_id, current_user_id, update_dict)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        logger.info(f"Successfully updated goal {goal_id} for user: {current_user_id}")
        
        return {
            "success": True,
            "data": goal.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating goal {goal_id} for user {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update goal")

@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a goal.
    """
    try:
        goal_service = GoalService(db)
        
        success = goal_service.delete_goal(goal_id, current_user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        logger.info(f"Successfully deleted goal {goal_id} for user: {current_user_id}")
        
        return {
            "success": True,
            "message": "Goal deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting goal {goal_id} for user {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete goal")

@router.post("/{goal_id}/progress")
async def add_goal_progress(
    goal_id: str,
    progress_data: GoalProgressAdd,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Add progress to a goal.
    """
    try:
        goal_service = GoalService(db)
        
        progress = goal_service.add_goal_progress(
            goal_id=goal_id,
            user_id=current_user_id,
            value=progress_data.value,
            notes=progress_data.notes
        )
        
        if not progress:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        logger.info(f"Successfully added progress to goal {goal_id} for user: {current_user_id}")
        
        return {
            "success": True,
            "data": {
                "id": str(progress.id),
                "value": progress.value,
                "notes": progress.notes,
                "date": progress.date.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding progress to goal {goal_id} for user {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add progress")

@router.get("/stats/summary")
async def get_goals_stats(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get user's goals statistics summary.
    """
    try:
        goal_service = GoalService(db)
        
        stats = goal_service.get_user_goal_stats(current_user_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Error fetching goal stats for user {current_user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch goal statistics")
