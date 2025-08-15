"""
AI Insights routes for Elevate AI
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database.utils import get_db
from schemas.ai_insight import AIInsightCreate, AIInsightOut
from models.ai_insight import AIInsight
from utils.auth import verify_token

router = APIRouter(prefix="/insights", tags=["AI Insights"])
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


@router.get("/", response_model=List[AIInsightOut])
async def get_insights(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of insights to return"),
    offset: int = Query(0, ge=0, description="Number of insights to skip"),
    insight_type: Optional[str] = Query(None, description="Filter by insight type")
):
    """
    Get user's AI insights with optional filtering
    """
    query = db.query(AIInsight).filter(AIInsight.user_id == uuid.UUID(current_user_id))
    
    # Filter by insight type if provided
    if insight_type:
        query = query.filter(AIInsight.insight_type == insight_type)
    
    # Order by generation date descending and apply pagination
    insights = query.order_by(AIInsight.generated_at.desc()).offset(offset).limit(limit).all()
    
    return [AIInsightOut.from_orm(insight) for insight in insights]


@router.get("/{insight_id}", response_model=AIInsightOut)
async def get_insight(
    insight_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific AI insight by ID
    """
    try:
        insight_uuid = uuid.UUID(insight_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid insight ID format"
        )
    
    insight = db.query(AIInsight).filter(
        AIInsight.id == insight_uuid,
        AIInsight.user_id == uuid.UUID(current_user_id)
    ).first()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI insight not found"
        )
    
    return AIInsightOut.from_orm(insight)


@router.post("/generate")
async def generate_insights(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Generate new AI insights based on user's activity data
    """
    try:
        # Get user's recent activity data for analysis
        from models.activity_log import ActivityLog
        from datetime import datetime, timezone, timedelta
        
        # Get activities from the last 30 days
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        activities = db.query(ActivityLog).filter(
            ActivityLog.user_id == uuid.UUID(current_user_id),
            ActivityLog.date >= start_date,
            ActivityLog.date <= end_date
        ).all()
        
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough activity data to generate insights"
            )
        
        # Generate mock insights (in production, this would use actual AI analysis)
        generated_insights = generate_mock_insights(current_user_id, activities)
        
        # Save insights to database
        db_insights = []
        for insight_data in generated_insights:
            insight_data["user_id"] = uuid.UUID(current_user_id)
            db_insight = AIInsight(**insight_data)
            db.add(db_insight)
            db_insights.append(db_insight)
        
        db.commit()
        
        # Refresh all insights
        for insight in db_insights:
            db.refresh(insight)
        
        return {
            "message": f"Generated {len(db_insights)} new insights",
            "insights": [AIInsightOut.from_orm(insight) for insight in db_insights]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )


@router.delete("/{insight_id}")
async def delete_insight(
    insight_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete an AI insight
    """
    try:
        insight_uuid = uuid.UUID(insight_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid insight ID format"
        )
    
    insight = db.query(AIInsight).filter(
        AIInsight.id == insight_uuid,
        AIInsight.user_id == uuid.UUID(current_user_id)
    ).first()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI insight not found"
        )
    
    try:
        db.delete(insight)
        db.commit()
        return {"message": "AI insight deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete insight: {str(e)}"
        )


def generate_mock_insights(user_id: str, activities: List) -> List[dict]:
    """
    Generate mock AI insights based on activity data
    In production, this would use actual AI analysis algorithms
    """
    insights = []
    
    # Productivity pattern insight
    insights.append({
        "insight_type": "productivity_pattern",
        "summary": "Your most productive hours are between 9-11 AM with an average productivity score of 8.5/10.",
        "suggestions": [
            "Schedule your most important tasks during 9-11 AM",
            "Avoid meetings during peak productivity hours",
            "Use this time for deep work and complex problem-solving"
        ]
    })
    
    # Energy optimization insight
    insights.append({
        "insight_type": "energy_optimization", 
        "summary": "You experience a consistent energy drop around 2-3 PM. A 15-minute walk could boost your energy by 20%.",
        "suggestions": [
            "Take a 15-minute walk after lunch",
            "Consider a healthy snack around 2 PM",
            "Schedule lighter tasks during this period"
        ]
    })
    
    # Activity frequency insight
    if len(activities) > 0:
        avg_activities_per_day = len(activities) / 30  # 30 days of data
        if avg_activities_per_day < 3:
            insights.append({
                "insight_type": "activity_frequency",
                "summary": f"You're logging {avg_activities_per_day:.1f} activities per day on average. Increasing activity tracking could provide better insights.",
                "suggestions": [
                    "Try to log at least 5 activities per day",
                    "Include smaller tasks and breaks in your tracking",
                    "Set reminders to log activities throughout the day"
                ]
            })
    
    # Work-life balance insight
    insights.append({
        "insight_type": "work_life_balance",
        "summary": "Based on your activity patterns, you spend 65% of tracked time on work activities. Consider allocating more time to personal activities.",
        "suggestions": [
            "Set boundaries for work hours",
            "Schedule regular personal time",
            "Increase health-related activities to 20%"
        ]
    })
    
    return insights


@router.get("/types/available")
async def get_available_insight_types():
    """
    Get list of available insight types
    """
    return {
        "insight_types": [
            {
                "type": "productivity_pattern",
                "name": "Productivity Patterns",
                "description": "Analyze your most productive times and patterns"
            },
            {
                "type": "energy_optimization",
                "name": "Energy Optimization", 
                "description": "Identify energy dips and optimization opportunities"
            },
            {
                "type": "activity_frequency",
                "name": "Activity Frequency",
                "description": "Track how often you log activities and suggest improvements"
            },
            {
                "type": "work_life_balance",
                "name": "Work-Life Balance",
                "description": "Analyze time allocation between work and personal activities"
            },
            {
                "type": "mood_correlation",
                "name": "Mood Correlations",
                "description": "Find correlations between activities and mood levels"
            },
            {
                "type": "goal_progress",
                "name": "Goal Progress",
                "description": "Track progress towards your personal and professional goals"
            }
        ]
    }
