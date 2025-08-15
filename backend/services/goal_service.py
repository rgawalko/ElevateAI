"""
Goal Service

Handles all goal-related business logic including goal management,
progress tracking, and goal analytics.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import uuid

from .base_service import BaseService
from models import Goal, GoalProgress


class GoalService(BaseService):
    """
    Service for goal management operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def create_goal(self, user_id: str, goal_data: Dict[str, Any]) -> Optional[Goal]:
        """
        Create a new goal for a user.
        """
        try:
            # Prepare goal data
            goal_data['user_id'] = uuid.UUID(user_id)
            
            # Set default values
            if 'current_value' not in goal_data:
                goal_data['current_value'] = 0.0
            
            if 'is_active' not in goal_data:
                goal_data['is_active'] = True
            
            # Create goal
            goal = Goal(**goal_data)
            self.db.add(goal)
            self.db.commit()
            self.db.refresh(goal)
            
            self.logger.info(f"Created goal '{goal.title}' for user {user_id}")
            return goal
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating goal: {e}")
            return None
    
    def get_user_goals(self, user_id: str, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get user's goals with filtering and pagination.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            query = self.db.query(Goal).options(
                joinedload(Goal.goal_progress)
            ).filter(Goal.user_id == uuid_id)
            
            # Apply filters
            if filters:
                if 'is_active' in filters and filters['is_active'] is not None:
                    query = query.filter(Goal.is_active == filters['is_active'])
                
                if 'is_completed' in filters and filters['is_completed'] is not None:
                    query = query.filter(Goal.is_completed == filters['is_completed'])
                
                if 'category' in filters and filters['category']:
                    query = query.filter(Goal.category == filters['category'])
                
                if 'overdue_only' in filters and filters['overdue_only']:
                    now = datetime.now(timezone.utc)
                    query = query.filter(
                        and_(
                            Goal.deadline.isnot(None),
                            Goal.deadline < now,
                            Goal.is_completed == False
                        )
                    )
            
            # Order by creation date descending
            query = query.order_by(desc(Goal.created_at))
            
            return self.paginate(query, page, per_page)
            
        except Exception as e:
            self.logger.error(f"Error getting user goals: {e}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "pages": 0}
    
    def get_goal_with_progress(self, goal_id: str, user_id: str) -> Optional[Goal]:
        """
        Get goal with progress history loaded.
        """
        try:
            uuid_goal_id = uuid.UUID(goal_id)
            uuid_user_id = uuid.UUID(user_id)
            
            return self.db.query(Goal).options(
                joinedload(Goal.goal_progress)
            ).filter(
                and_(
                    Goal.id == uuid_goal_id,
                    Goal.user_id == uuid_user_id
                )
            ).first()
            
        except Exception as e:
            self.logger.error(f"Error getting goal with progress: {e}")
            return None
    
    def update_goal(self, goal_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Goal]:
        """
        Update goal information.
        """
        try:
            goal = self.get_goal_with_progress(goal_id, user_id)
            if not goal:
                return None
            
            # Handle completion status change
            if 'is_completed' in update_data and update_data['is_completed'] and not goal.is_completed:
                update_data['completed_at'] = datetime.now(timezone.utc)
            elif 'is_completed' in update_data and not update_data['is_completed'] and goal.is_completed:
                update_data['completed_at'] = None
            
            return self.update(goal, update_data)
            
        except Exception as e:
            self.logger.error(f"Error updating goal: {e}")
            return None
    
    def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """
        Delete goal and all associated progress records.
        """
        try:
            goal = self.get_goal_with_progress(goal_id, user_id)
            if not goal:
                return False
            
            return self.delete(goal)
            
        except Exception as e:
            self.logger.error(f"Error deleting goal: {e}")
            return False
    
    def add_goal_progress(self, goal_id: str, user_id: str, value: float, notes: str = None) -> Optional[GoalProgress]:
        """
        Add progress entry to a goal and update current value.
        """
        try:
            goal = self.get_goal_with_progress(goal_id, user_id)
            if not goal:
                return None
            
            # Create progress entry
            progress_data = {
                'goal_id': uuid.UUID(goal_id),
                'user_id': uuid.UUID(user_id),
                'value': value,
                'notes': notes
            }
            
            progress = GoalProgress(**progress_data)
            self.db.add(progress)
            
            # Update goal's current value
            goal.current_value = value
            
            # Check if goal is completed
            if value >= goal.target_value and not goal.is_completed:
                goal.is_completed = True
                goal.completed_at = datetime.now(timezone.utc)
            
            self.db.commit()
            self.db.refresh(progress)
            
            self.logger.info(f"Added progress to goal '{goal.title}': {value}/{goal.target_value}")
            return progress
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error adding goal progress: {e}")
            return None
    
    def get_goal_progress_history(self, goal_id: str, user_id: str, limit: int = 50) -> List[GoalProgress]:
        """
        Get progress history for a goal.
        """
        try:
            uuid_goal_id = uuid.UUID(goal_id)
            uuid_user_id = uuid.UUID(user_id)
            
            # Verify goal belongs to user
            goal = self.db.query(Goal).filter(
                and_(Goal.id == uuid_goal_id, Goal.user_id == uuid_user_id)
            ).first()
            
            if not goal:
                return []
            
            progress_entries = self.db.query(GoalProgress).filter(
                GoalProgress.goal_id == uuid_goal_id
            ).order_by(desc(GoalProgress.date)).limit(limit).all()
            
            return progress_entries
            
        except Exception as e:
            self.logger.error(f"Error getting goal progress history: {e}")
            return []
    
    def get_goal_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive goal statistics for a user.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            
            # Get basic counts
            total_goals = self.db.query(Goal).filter(Goal.user_id == uuid_id).count()
            active_goals = self.db.query(Goal).filter(
                and_(Goal.user_id == uuid_id, Goal.is_active == True)
            ).count()
            completed_goals = self.db.query(Goal).filter(
                and_(Goal.user_id == uuid_id, Goal.is_completed == True)
            ).count()
            
            # Get overdue goals
            now = datetime.now(timezone.utc)
            overdue_goals = self.db.query(Goal).filter(
                and_(
                    Goal.user_id == uuid_id,
                    Goal.deadline.isnot(None),
                    Goal.deadline < now,
                    Goal.is_completed == False
                )
            ).count()
            
            # Get goals by category
            category_stats = self.db.query(
                Goal.category,
                func.count(Goal.id).label('count')
            ).filter(Goal.user_id == uuid_id).group_by(Goal.category).all()
            
            # Calculate completion rate
            completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
            
            # Get recent progress (last 30 days)
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent_progress_count = self.db.query(GoalProgress).filter(
                and_(
                    GoalProgress.user_id == uuid_id,
                    GoalProgress.created_at >= thirty_days_ago
                )
            ).count()
            
            # Get average progress per goal
            goals_with_progress = self.db.query(Goal).filter(
                and_(Goal.user_id == uuid_id, Goal.current_value > 0)
            ).all()
            
            avg_progress = sum(g.progress_percentage for g in goals_with_progress) / max(len(goals_with_progress), 1)
            
            return {
                "total_goals": total_goals,
                "active_goals": active_goals,
                "completed_goals": completed_goals,
                "overdue_goals": overdue_goals,
                "completion_rate": round(completion_rate, 1),
                "average_progress": round(avg_progress, 1),
                "recent_progress_entries": recent_progress_count,
                "categories": [
                    {"category": category, "count": count}
                    for category, count in category_stats
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting goal statistics: {e}")
            return {}
    
    def get_goal_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get AI-powered goal recommendations.
        """
        try:
            # Get user's goal statistics
            stats = self.get_goal_statistics(user_id)
            
            recommendations = []
            
            # Recommend based on completion rate
            completion_rate = stats.get("completion_rate", 0)
            if completion_rate < 50:
                recommendations.append({
                    "type": "goal_setting",
                    "title": "Set More Achievable Goals",
                    "description": "Consider breaking large goals into smaller, more manageable milestones",
                    "priority": "high"
                })
            
            # Recommend based on overdue goals
            overdue_count = stats.get("overdue_goals", 0)
            if overdue_count > 0:
                recommendations.append({
                    "type": "deadline_management",
                    "title": "Review Overdue Goals",
                    "description": f"You have {overdue_count} overdue goals. Consider extending deadlines or breaking them down",
                    "priority": "high"
                })
            
            # Recommend based on progress tracking
            recent_progress = stats.get("recent_progress_entries", 0)
            if recent_progress < 5:
                recommendations.append({
                    "type": "progress_tracking",
                    "title": "Track Progress More Frequently",
                    "description": "Regular progress updates help maintain motivation and momentum",
                    "priority": "medium"
                })
            
            # Recommend goal categories
            categories = stats.get("categories", [])
            if len(categories) < 3:
                recommendations.append({
                    "type": "goal_diversity",
                    "title": "Diversify Your Goals",
                    "description": "Consider setting goals in different areas like health, career, and personal development",
                    "priority": "low"
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting goal recommendations: {e}")
            return []
    
    def get_upcoming_deadlines(self, user_id: str, days: int = 7) -> List[Goal]:
        """
        Get goals with upcoming deadlines.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            now = datetime.now(timezone.utc)
            end_date = now + timedelta(days=days)
            
            goals = self.db.query(Goal).filter(
                and_(
                    Goal.user_id == uuid_id,
                    Goal.deadline.isnot(None),
                    Goal.deadline >= now,
                    Goal.deadline <= end_date,
                    Goal.is_completed == False
                )
            ).order_by(Goal.deadline).all()
            
            return goals
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming deadlines: {e}")
            return []
