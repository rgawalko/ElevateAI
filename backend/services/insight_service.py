"""
Insight Service

Handles all AI insight-related business logic including insight generation,
user actions tracking, and insight analytics.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import uuid

from .base_service import BaseService
from .activity_service import ActivityService
from .schedule_service import ScheduleService
from .goal_service import GoalService
from models import AIInsight, InsightAction, ActivityLog, Schedule, Goal


class InsightService(BaseService):
    """
    Service for AI insight management operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.activity_service = ActivityService(db)
        self.schedule_service = ScheduleService(db)
        self.goal_service = GoalService(db)
    
    def generate_insights(self, user_id: str) -> List[AIInsight]:
        """
        Generate new AI insights based on user's data.
        """
        try:
            # Get user's recent data for analysis
            activity_stats = self.activity_service.get_activity_statistics(user_id, days=30)
            schedule_stats = self.schedule_service.get_schedule_statistics(user_id, days=30)
            goal_stats = self.goal_service.get_goal_statistics(user_id)
            
            # Generate insights based on data analysis
            insights_data = self._analyze_user_data(user_id, activity_stats, schedule_stats, goal_stats)
            
            # Create insight records
            insights = []
            for insight_data in insights_data:
                insight_data['user_id'] = uuid.UUID(user_id)
                insight = AIInsight(**insight_data)
                self.db.add(insight)
                insights.append(insight)
            
            self.db.commit()
            
            # Refresh all insights
            for insight in insights:
                self.db.refresh(insight)
            
            self.logger.info(f"Generated {len(insights)} insights for user {user_id}")
            return insights
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error generating insights: {e}")
            return []
    
    def _analyze_user_data(self, user_id: str, activity_stats: Dict, schedule_stats: Dict, goal_stats: Dict) -> List[Dict[str, Any]]:
        """
        Analyze user data and generate insight data.
        """
        insights = []
        
        # Productivity pattern insight
        avg_activities = activity_stats.get("average_per_day", 0)
        if avg_activities > 0:
            if avg_activities >= 5:
                productivity_level = "high"
                message = f"You're maintaining excellent productivity with {avg_activities:.1f} activities per day on average."
            elif avg_activities >= 3:
                productivity_level = "moderate"
                message = f"You're tracking {avg_activities:.1f} activities per day. Consider increasing to 5+ for better insights."
            else:
                productivity_level = "low"
                message = f"You're tracking only {avg_activities:.1f} activities per day. More tracking will provide better insights."
            
            insights.append({
                "insight_type": "productivity_pattern",
                "summary": message,
                "suggestions": self._get_productivity_suggestions(productivity_level)
            })
        
        # Schedule optimization insight
        completion_rate = schedule_stats.get("completion_rate", 0)
        if completion_rate > 0:
            if completion_rate >= 80:
                insights.append({
                    "insight_type": "schedule_optimization",
                    "summary": f"Excellent task completion rate of {completion_rate}%! You're managing your schedule effectively.",
                    "suggestions": [
                        "Continue your current scheduling approach",
                        "Consider taking on more challenging tasks",
                        "Share your scheduling strategies with others"
                    ]
                })
            elif completion_rate >= 60:
                insights.append({
                    "insight_type": "schedule_optimization",
                    "summary": f"Good task completion rate of {completion_rate}%. There's room for improvement.",
                    "suggestions": [
                        "Review incomplete tasks to identify patterns",
                        "Consider breaking large tasks into smaller ones",
                        "Set more realistic time estimates"
                    ]
                })
            else:
                insights.append({
                    "insight_type": "schedule_optimization",
                    "summary": f"Task completion rate of {completion_rate}% suggests scheduling challenges.",
                    "suggestions": [
                        "Reduce the number of tasks per day",
                        "Focus on 3-5 high-priority tasks daily",
                        "Build buffer time between tasks",
                        "Consider using AI schedule generation"
                    ]
                })
        
        # Goal progress insight
        goal_completion_rate = goal_stats.get("completion_rate", 0)
        active_goals = goal_stats.get("active_goals", 0)
        
        if active_goals > 0:
            if goal_completion_rate >= 70:
                insights.append({
                    "insight_type": "goal_progress",
                    "summary": f"Strong goal achievement with {goal_completion_rate}% completion rate across {active_goals} active goals.",
                    "suggestions": [
                        "Maintain your current goal-setting approach",
                        "Consider setting more ambitious goals",
                        "Help others with goal achievement strategies"
                    ]
                })
            elif goal_completion_rate >= 40:
                insights.append({
                    "insight_type": "goal_progress",
                    "summary": f"Moderate goal progress with {goal_completion_rate}% completion rate. Focus on consistency.",
                    "suggestions": [
                        "Break large goals into smaller milestones",
                        "Set weekly progress check-ins",
                        "Celebrate small wins along the way"
                    ]
                })
            else:
                insights.append({
                    "insight_type": "goal_progress",
                    "summary": f"Goal completion rate of {goal_completion_rate}% indicates need for strategy adjustment.",
                    "suggestions": [
                        "Review and simplify your goals",
                        "Focus on 1-2 goals at a time",
                        "Set more achievable deadlines",
                        "Track progress more frequently"
                    ]
                })
        
        # Work-life balance insight
        activity_frequency = activity_stats.get("activity_frequency", 0)
        if activity_frequency > 80:
            insights.append({
                "insight_type": "work_life_balance",
                "summary": f"High activity frequency of {activity_frequency}% suggests you're very busy. Consider balance.",
                "suggestions": [
                    "Schedule regular breaks and downtime",
                    "Delegate tasks when possible",
                    "Practice saying no to non-essential commitments",
                    "Prioritize self-care activities"
                ]
            })
        elif activity_frequency < 30:
            insights.append({
                "insight_type": "work_life_balance",
                "summary": f"Low activity frequency of {activity_frequency}% might indicate missed tracking opportunities.",
                "suggestions": [
                    "Set reminders to log activities",
                    "Include personal and leisure activities",
                    "Track smaller tasks and breaks",
                    "Use activity templates for common tasks"
                ]
            })
        
        return insights
    
    def _get_productivity_suggestions(self, level: str) -> List[str]:
        """Get productivity suggestions based on level."""
        if level == "high":
            return [
                "Maintain your excellent tracking habits",
                "Consider mentoring others on productivity",
                "Experiment with advanced productivity techniques",
                "Share your success strategies"
            ]
        elif level == "moderate":
            return [
                "Aim to track 5+ activities per day",
                "Include smaller tasks and breaks",
                "Set activity tracking reminders",
                "Use templates for recurring activities"
            ]
        else:
            return [
                "Start with tracking 3 main activities daily",
                "Set hourly reminders to log activities",
                "Focus on work, personal, and health activities",
                "Use simple activity descriptions initially"
            ]
    
    def get_user_insights(self, user_id: str, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get user's insights with filtering and pagination.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            query = self.db.query(AIInsight).options(
                joinedload(AIInsight.insight_actions)
            ).filter(AIInsight.user_id == uuid_id)
            
            # Apply filters
            if filters:
                if 'insight_type' in filters and filters['insight_type']:
                    query = query.filter(AIInsight.insight_type == filters['insight_type'])
                
                if 'start_date' in filters and filters['start_date']:
                    query = query.filter(AIInsight.generated_at >= filters['start_date'])
                
                if 'end_date' in filters and filters['end_date']:
                    query = query.filter(AIInsight.generated_at <= filters['end_date'])
            
            # Order by generation date descending
            query = query.order_by(desc(AIInsight.generated_at))
            
            return self.paginate(query, page, per_page)
            
        except Exception as e:
            self.logger.error(f"Error getting user insights: {e}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "pages": 0}
    
    def get_insight_with_actions(self, insight_id: str, user_id: str) -> Optional[AIInsight]:
        """
        Get insight with actions loaded.
        """
        try:
            uuid_insight_id = uuid.UUID(insight_id)
            uuid_user_id = uuid.UUID(user_id)
            
            return self.db.query(AIInsight).options(
                joinedload(AIInsight.insight_actions)
            ).filter(
                and_(
                    AIInsight.id == uuid_insight_id,
                    AIInsight.user_id == uuid_user_id
                )
            ).first()
            
        except Exception as e:
            self.logger.error(f"Error getting insight with actions: {e}")
            return None
    
    def delete_insight(self, insight_id: str, user_id: str) -> bool:
        """
        Delete insight and all associated actions.
        """
        try:
            insight = self.get_insight_with_actions(insight_id, user_id)
            if not insight:
                return False
            
            return self.delete(insight)
            
        except Exception as e:
            self.logger.error(f"Error deleting insight: {e}")
            return False
    
    def record_insight_action(self, insight_id: str, user_id: str, action_type: str, action_data: str = None, notes: str = None) -> Optional[InsightAction]:
        """
        Record user action on an insight.
        """
        try:
            # Verify insight belongs to user
            insight = self.get_insight_with_actions(insight_id, user_id)
            if not insight:
                return None
            
            action_data_dict = {
                'insight_id': uuid.UUID(insight_id),
                'user_id': uuid.UUID(user_id),
                'action_type': action_type,
                'action_data': action_data,
                'notes': notes
            }
            
            action = InsightAction(**action_data_dict)
            self.db.add(action)
            self.db.commit()
            self.db.refresh(action)
            
            self.logger.info(f"Recorded {action_type} action on insight {insight_id}")
            return action
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error recording insight action: {e}")
            return None
    
    def get_insight_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get insight statistics for a user.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            
            # Get total insights
            total_insights = self.db.query(AIInsight).filter(AIInsight.user_id == uuid_id).count()
            
            # Get insights by type
            insight_types = self.db.query(
                AIInsight.insight_type,
                func.count(AIInsight.id).label('count')
            ).filter(AIInsight.user_id == uuid_id).group_by(AIInsight.insight_type).all()
            
            # Get recent insights (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_insights = self.db.query(AIInsight).filter(
                and_(
                    AIInsight.user_id == uuid_id,
                    AIInsight.generated_at >= thirty_days_ago
                )
            ).count()
            
            # Get action statistics
            total_actions = self.db.query(InsightAction).filter(InsightAction.user_id == uuid_id).count()
            
            action_types = self.db.query(
                InsightAction.action_type,
                func.count(InsightAction.id).label('count')
            ).filter(InsightAction.user_id == uuid_id).group_by(InsightAction.action_type).all()
            
            return {
                "total_insights": total_insights,
                "recent_insights": recent_insights,
                "total_actions": total_actions,
                "engagement_rate": (total_actions / max(total_insights, 1)) * 100,
                "insight_types": [
                    {"type": insight_type, "count": count}
                    for insight_type, count in insight_types
                ],
                "action_types": [
                    {"type": action_type, "count": count}
                    for action_type, count in action_types
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting insight statistics: {e}")
            return {}
    
    def get_available_insight_types(self) -> List[Dict[str, str]]:
        """
        Get list of available insight types.
        """
        return [
            {
                "type": "productivity_pattern",
                "name": "Productivity Patterns",
                "description": "Analyze your most productive times and patterns"
            },
            {
                "type": "schedule_optimization",
                "name": "Schedule Optimization",
                "description": "Optimize your daily schedule for better efficiency"
            },
            {
                "type": "goal_progress",
                "name": "Goal Progress",
                "description": "Track progress towards your personal and professional goals"
            },
            {
                "type": "work_life_balance",
                "name": "Work-Life Balance",
                "description": "Analyze time allocation between work and personal activities"
            },
            {
                "type": "energy_optimization",
                "name": "Energy Optimization",
                "description": "Identify energy dips and optimization opportunities"
            },
            {
                "type": "habit_formation",
                "name": "Habit Formation",
                "description": "Track and improve habit consistency"
            }
        ]
