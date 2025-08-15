"""
Schedule management routes for Elevate AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid
import logging

from database.utils import get_db
from schemas.schedule import ScheduleCreate, ScheduleOut
from models.schedule import Schedule
from utils.auth import verify_token
from services.ai_service import AIService

router = APIRouter(prefix="/schedules", tags=["Schedules"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


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


@router.post("/", response_model=ScheduleOut)
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new schedule
    """
    # Ensure the schedule belongs to the current user
    schedule_dict = schedule_data.dict()
    schedule_dict["user_id"] = uuid.UUID(current_user_id)
    
    db_schedule = Schedule(**schedule_dict)
    
    try:
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return ScheduleOut.from_orm(db_schedule)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {str(e)}"
        )


@router.get("/", response_model=List[ScheduleOut])
async def get_schedules(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = Query(30, ge=1, le=100, description="Number of schedules to return"),
    offset: int = Query(0, ge=0, description="Number of schedules to skip"),
    start_date: Optional[date] = Query(None, description="Filter schedules from this date"),
    end_date: Optional[date] = Query(None, description="Filter schedules until this date"),
    ai_generated: Optional[bool] = Query(None, description="Filter by AI-generated schedules")
):
    """
    Get user's schedules with optional filtering
    """
    query = db.query(Schedule).filter(Schedule.user_id == uuid.UUID(current_user_id))
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Schedule.date >= start_date)
    if end_date:
        query = query.filter(Schedule.date <= end_date)
    
    # Filter by AI-generated if specified
    if ai_generated is not None:
        query = query.filter(Schedule.generated_by_ai == ai_generated)
    
    # Order by date descending and apply pagination
    schedules = query.order_by(Schedule.date.desc()).offset(offset).limit(limit).all()
    
    return [ScheduleOut.from_orm(schedule) for schedule in schedules]


@router.get("/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(
    schedule_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific schedule by ID
    """
    try:
        schedule_uuid = uuid.UUID(schedule_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid schedule ID format"
        )
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_uuid,
        Schedule.user_id == uuid.UUID(current_user_id)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    return ScheduleOut.from_orm(schedule)


@router.put("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: str,
    schedule_update: ScheduleCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update an existing schedule
    """
    try:
        schedule_uuid = uuid.UUID(schedule_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid schedule ID format"
        )
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_uuid,
        Schedule.user_id == uuid.UUID(current_user_id)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Update schedule fields
    update_data = schedule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != "user_id" and hasattr(schedule, field):  # Don't allow user_id changes
            setattr(schedule, field, value)
    
    try:
        db.commit()
        db.refresh(schedule)
        return ScheduleOut.from_orm(schedule)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update schedule: {str(e)}"
        )


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a schedule
    """
    try:
        schedule_uuid = uuid.UUID(schedule_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid schedule ID format"
        )
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_uuid,
        Schedule.user_id == uuid.UUID(current_user_id)
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    try:
        db.delete(schedule)
        db.commit()
        return {"message": "Schedule deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete schedule: {str(e)}"
        )


# AI Schedule Generation Endpoint (Test Version - No Auth)
@router.post("/ai/generate-schedule-test")
async def generate_ai_schedule_test(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Test version of AI schedule generation without authentication
    """
    try:
        logger.info(f"Received AI schedule generation request: {request_data}")

        # Validate required fields
        if not request_data.get("activities"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Activities list is required"
            )

        # Use AI service for schedule generation
        ai_service = AIService(db)
        # Use a test user ID for now
        test_user_id = "test-user-123"
        result = ai_service.generate_optimized_schedule(test_user_id, request_data)

        if result.get("success"):
            return {
                "success": True,
                "schedule": result["schedule"],
                "schedule_id": result.get("schedule_id"),
                "message": result.get("message", "Schedule generated successfully"),
                "source": "azure_ai_agent"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Failed to generate schedule"),
                "message": "Schedule generation failed"
            }

    except Exception as e:
        logger.error(f"Error in AI schedule generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI schedule: {str(e)}"
        )


# AI Schedule Generation Endpoint (Original with Auth)
@router.post("/ai/generate-schedule")
async def generate_ai_schedule(
    request_data: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Generate an AI-optimized schedule based on user preferences

    Expected request format:
    {
        "date": "2025-08-01",
        "wakeUpTime": "07:00",
        "activities": [
            {"name": "Email review", "durationMinutes": 30, "priority": 2},
            {"name": "Team meeting", "durationMinutes": 60, "priority": 1, "timeWindow": ["09:00","11:00"]},
            {"name": "Project work", "durationMinutes": 180, "priority": 3},
            {"name": "Gym", "durationMinutes": 45, "priority": 4}
        ],
        "constraints": {
            "lunchBreak": true,
            "maxConsecutiveWorkHours": 4
        }
    }
    """
    try:
        # Validate required fields
        required_fields = ["date", "wakeUpTime", "activities", "constraints"]
        for field in required_fields:
            if field not in request_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        # Validate activities
        activities = request_data.get("activities", [])
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one activity is required"
            )

        for i, activity in enumerate(activities):
            required_activity_fields = ["name", "durationMinutes", "priority"]
            for field in required_activity_fields:
                if field not in activity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Activity {i+1} missing required field: {field}"
                    )

        # Use AI service for schedule generation
        ai_service = AIService(db)
        # Use a test user ID for now (in production, use current_user_id)
        test_user_id = "test-user-123"
        result = ai_service.generate_optimized_schedule(test_user_id, request_data)

        if result.get("success"):
            return {
                "success": True,
                "schedule": result["schedule"],
                "schedule_id": result.get("schedule_id"),
                "message": result.get("message", "Schedule generated successfully"),
                "source": "azure_ai_agent"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to generate schedule")
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate schedule: {str(e)}"
        )


def generate_mock_schedule(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mock AI schedule generation logic
    In production, this would be replaced with actual AI scheduling algorithms
    """
    # Import not needed for this mock implementation

    activities = request_data["activities"]
    constraints = request_data["constraints"]
    wake_time = request_data["wakeUpTime"]

    # Sort activities by priority (1 = highest priority)
    sorted_activities = sorted(activities, key=lambda x: x["priority"])

    # Parse wake up time
    wake_hour, wake_minute = map(int, wake_time.split(":"))
    work_start_time = f"{wake_hour + 1:02d}:{wake_minute:02d}"

    scheduled_activities = []
    current_time = work_start_time
    consecutive_work_time = 0
    lunch_scheduled = False

    def add_minutes_to_time(time_str: str, minutes: int) -> str:
        hour, minute = map(int, time_str.split(":"))
        total_minutes = hour * 60 + minute + minutes
        new_hour = (total_minutes // 60) % 24
        new_minute = total_minutes % 60
        return f"{new_hour:02d}:{new_minute:02d}"

    def time_to_minutes(time_str: str) -> int:
        hour, minute = map(int, time_str.split(":"))
        return hour * 60 + minute

    for activity in sorted_activities:
        # Check if we need a lunch break
        if (constraints.get("lunchBreak", True) and not lunch_scheduled and
            time_to_minutes(current_time) >= 12 * 60):  # After 12:00 PM

            lunch_duration = 60
            scheduled_activities.append({
                "name": "Lunch Break",
                "startTime": current_time,
                "endTime": add_minutes_to_time(current_time, lunch_duration),
                "durationMinutes": lunch_duration,
                "priority": 0,
                "category": "break"
            })
            current_time = add_minutes_to_time(current_time, lunch_duration)
            lunch_scheduled = True
            consecutive_work_time = 0

        # Check consecutive work hours limit
        max_consecutive_hours = constraints.get("maxConsecutiveWorkHours", 4)
        if consecutive_work_time >= max_consecutive_hours * 60:
            break_duration = 30
            scheduled_activities.append({
                "name": "Break",
                "startTime": current_time,
                "endTime": add_minutes_to_time(current_time, break_duration),
                "durationMinutes": break_duration,
                "priority": 0,
                "category": "break"
            })
            current_time = add_minutes_to_time(current_time, break_duration)
            consecutive_work_time = 0

        # Schedule the activity
        end_time = add_minutes_to_time(current_time, activity["durationMinutes"])
        scheduled_activities.append({
            "name": activity["name"],
            "startTime": current_time,
            "endTime": end_time,
            "durationMinutes": activity["durationMinutes"],
            "priority": activity["priority"],
            "category": activity.get("category", "work")
        })

        current_time = end_time
        consecutive_work_time += activity["durationMinutes"]

    total_duration = sum(act["durationMinutes"] for act in scheduled_activities)

    return {
        "date": request_data["date"],
        "totalDuration": total_duration,
        "scheduledActivities": scheduled_activities,
        "unscheduledActivities": [],
        "breaks": [act for act in scheduled_activities if act.get("category") == "break"],
        "summary": {
            "totalWorkTime": sum(act["durationMinutes"] for act in scheduled_activities if act.get("category") != "break"),
            "totalBreakTime": sum(act["durationMinutes"] for act in scheduled_activities if act.get("category") == "break"),
            "totalFreeTime": max(0, 8 * 60 - total_duration),
            "productivityScore": 85,
            "balanceScore": 78
        }
    }
