"""
Activity management routes for Elevate AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database.utils import get_db
from schemas.activity_log import ActivityLogCreate, ActivityLogOut
from models.activity_log import ActivityLog
from utils.auth import verify_token

router = APIRouter(prefix="/activities", tags=["Activities"])
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
            detail="Invalid or expired access token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return user_id


@router.post("/", response_model=ActivityLogOut)
async def create_activity_log(
    activity_data: ActivityLogCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new activity log entry
    """
    # Ensure the activity belongs to the current user
    activity_dict = activity_data.dict()
    activity_dict["user_id"] = uuid.UUID(current_user_id)
    
    db_activity = ActivityLog(**activity_dict)
    
    try:
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return ActivityLogOut.from_orm(db_activity)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create activity log: {str(e)}"
        )


@router.get("/", response_model=List[ActivityLogOut])
async def get_activity_logs(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="Number of activities to return"),
    offset: int = Query(0, ge=0, description="Number of activities to skip"),
    start_date: Optional[datetime] = Query(None, description="Filter activities from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter activities until this date")
):
    """
    Get user's activity logs with optional filtering
    """
    query = db.query(ActivityLog).filter(ActivityLog.user_id == uuid.UUID(current_user_id))
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(ActivityLog.date >= start_date)
    if end_date:
        query = query.filter(ActivityLog.date <= end_date)
    
    # Order by date descending and apply pagination
    activities = query.order_by(ActivityLog.date.desc()).offset(offset).limit(limit).all()
    
    return [ActivityLogOut.from_orm(activity) for activity in activities]


@router.get("/{activity_id}", response_model=ActivityLogOut)
async def get_activity_log(
    activity_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific activity log by ID
    """
    try:
        activity_uuid = uuid.UUID(activity_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activity ID format"
        )
    
    activity = db.query(ActivityLog).filter(
        ActivityLog.id == activity_uuid,
        ActivityLog.user_id == uuid.UUID(current_user_id)
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found"
        )
    
    return ActivityLogOut.from_orm(activity)


@router.put("/{activity_id}", response_model=ActivityLogOut)
async def update_activity_log(
    activity_id: str,
    activity_update: ActivityLogCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update an existing activity log
    """
    try:
        activity_uuid = uuid.UUID(activity_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activity ID format"
        )
    
    activity = db.query(ActivityLog).filter(
        ActivityLog.id == activity_uuid,
        ActivityLog.user_id == uuid.UUID(current_user_id)
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found"
        )
    
    # Update activity fields
    update_data = activity_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != "user_id" and hasattr(activity, field):  # Don't allow user_id changes
            setattr(activity, field, value)
    
    try:
        db.commit()
        db.refresh(activity)
        return ActivityLogOut.from_orm(activity)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update activity log: {str(e)}"
        )


@router.delete("/{activity_id}")
async def delete_activity_log(
    activity_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete an activity log
    """
    try:
        activity_uuid = uuid.UUID(activity_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activity ID format"
        )
    
    activity = db.query(ActivityLog).filter(
        ActivityLog.id == activity_uuid,
        ActivityLog.user_id == uuid.UUID(current_user_id)
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found"
        )
    
    try:
        db.delete(activity)
        db.commit()
        return {"message": "Activity log deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete activity log: {str(e)}"
        )


@router.get("/stats/summary")
async def get_activity_summary(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary")
):
    """
    Get activity summary statistics for the specified number of days
    """
    from datetime import datetime, timedelta, timezone
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == uuid.UUID(current_user_id),
        ActivityLog.date >= start_date,
        ActivityLog.date <= end_date
    ).all()
    
    # Calculate summary statistics
    total_activities = len(activities)
    total_days = days
    
    # Group activities by date for daily averages
    daily_counts = {}
    for activity in activities:
        date_key = activity.date.date()
        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
    
    avg_activities_per_day = sum(daily_counts.values()) / max(len(daily_counts), 1)
    
    return {
        "period_days": days,
        "total_activities": total_activities,
        "average_activities_per_day": round(avg_activities_per_day, 2),
        "active_days": len(daily_counts),
        "activity_frequency": round(len(daily_counts) / total_days * 100, 1)  # percentage
    }
