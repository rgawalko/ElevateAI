"""
Activity Service

Handles all activity-related business logic including activity logging,
tagging, and analytics.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import uuid

from .base_service import BaseService
from models import ActivityLog, ActivityTag, Tag


class ActivityService(BaseService):
    """
    Service for activity management operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def create_activity_log(self, user_id: str, activity_data: Dict[str, Any], tag_names: List[str] = None) -> Optional[ActivityLog]:
        """
        Create a new activity log with optional tags.
        """
        try:
            # Prepare activity data
            activity_data['user_id'] = uuid.UUID(user_id)
            
            # Create activity log
            activity = ActivityLog(**activity_data)
            self.db.add(activity)
            self.db.flush()  # Get activity ID
            
            # Add tags if provided
            if tag_names:
                from .tag_service import TagService
                tag_service = TagService(self.db)
                
                for tag_name in tag_names:
                    tag = tag_service.get_or_create_tag(user_id, tag_name)
                    if tag:
                        activity_tag = ActivityTag(
                            activity_log_id=activity.id,
                            tag_id=tag.id
                        )
                        self.db.add(activity_tag)
            
            self.db.commit()
            self.db.refresh(activity)
            
            self.logger.info(f"Created activity log for user {user_id}")
            return activity
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating activity log: {e}")
            return None
    
    def get_user_activities(self, user_id: str, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get user's activity logs with filtering and pagination.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            query = self.db.query(ActivityLog).options(
                joinedload(ActivityLog.activity_tags).joinedload(ActivityTag.tag)
            ).filter(ActivityLog.user_id == uuid_id)
            
            # Apply filters
            if filters:
                if 'start_date' in filters and filters['start_date']:
                    query = query.filter(ActivityLog.date >= filters['start_date'])
                
                if 'end_date' in filters and filters['end_date']:
                    query = query.filter(ActivityLog.date <= filters['end_date'])
                
                if 'tag_names' in filters and filters['tag_names']:
                    # Filter by tag names
                    query = query.join(ActivityTag).join(Tag).filter(
                        Tag.name.in_(filters['tag_names'])
                    )
            
            # Order by date descending
            query = query.order_by(desc(ActivityLog.date))
            
            return self.paginate(query, page, per_page)
            
        except Exception as e:
            self.logger.error(f"Error getting user activities: {e}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "pages": 0}
    
    def get_activity_with_tags(self, activity_id: str, user_id: str) -> Optional[ActivityLog]:
        """
        Get activity log with tags loaded.
        """
        try:
            uuid_activity_id = uuid.UUID(activity_id)
            uuid_user_id = uuid.UUID(user_id)
            
            return self.db.query(ActivityLog).options(
                joinedload(ActivityLog.activity_tags).joinedload(ActivityTag.tag)
            ).filter(
                and_(
                    ActivityLog.id == uuid_activity_id,
                    ActivityLog.user_id == uuid_user_id
                )
            ).first()
            
        except Exception as e:
            self.logger.error(f"Error getting activity with tags: {e}")
            return None
    
    def update_activity_log(self, activity_id: str, user_id: str, update_data: Dict[str, Any], tag_names: List[str] = None) -> Optional[ActivityLog]:
        """
        Update activity log and optionally update tags.
        """
        try:
            activity = self.get_activity_with_tags(activity_id, user_id)
            if not activity:
                return None
            
            # Update activity fields
            for field, value in update_data.items():
                if hasattr(activity, field) and field not in ['id', 'user_id', 'created_at']:
                    setattr(activity, field, value)
            
            # Update tags if provided
            if tag_names is not None:
                # Remove existing tags
                self.db.query(ActivityTag).filter(
                    ActivityTag.activity_log_id == activity.id
                ).delete()
                
                # Add new tags
                from .tag_service import TagService
                tag_service = TagService(self.db)
                
                for tag_name in tag_names:
                    tag = tag_service.get_or_create_tag(user_id, tag_name)
                    if tag:
                        activity_tag = ActivityTag(
                            activity_log_id=activity.id,
                            tag_id=tag.id
                        )
                        self.db.add(activity_tag)
            
            self.db.commit()
            self.db.refresh(activity)
            return activity
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating activity log: {e}")
            return None
    
    def delete_activity_log(self, activity_id: str, user_id: str) -> bool:
        """
        Delete activity log and associated tags.
        """
        try:
            activity = self.get_activity_with_tags(activity_id, user_id)
            if not activity:
                return False
            
            return self.delete(activity)
            
        except Exception as e:
            self.logger.error(f"Error deleting activity log: {e}")
            return False
    
    def get_activity_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get activity statistics for the specified number of days.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Get activities in date range
            activities = self.db.query(ActivityLog).filter(
                and_(
                    ActivityLog.user_id == uuid_id,
                    ActivityLog.date >= start_date,
                    ActivityLog.date <= end_date
                )
            ).all()
            
            # Calculate statistics
            total_activities = len(activities)
            
            # Group by date for daily counts
            daily_counts = {}
            for activity in activities:
                date_key = activity.date.date()
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            
            # Calculate averages
            active_days = len(daily_counts)
            avg_per_day = total_activities / max(active_days, 1)
            activity_frequency = active_days / days * 100  # percentage of days with activities
            
            # Get most common tags
            tag_counts = {}
            for activity in activities:
                for activity_tag in activity.activity_tags:
                    tag_name = activity_tag.tag.name
                    tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
            
            # Sort tags by frequency
            popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "period_days": days,
                "total_activities": total_activities,
                "active_days": active_days,
                "average_per_day": round(avg_per_day, 2),
                "activity_frequency": round(activity_frequency, 1),
                "popular_tags": [{"name": name, "count": count} for name, count in popular_tags],
                "daily_breakdown": [
                    {"date": str(date), "count": count} 
                    for date, count in sorted(daily_counts.items())
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting activity statistics: {e}")
            return {}
    
    def get_activity_trends(self, user_id: str, days: int = 90) -> Dict[str, Any]:
        """
        Get activity trends over time.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Get weekly activity counts
            weekly_data = self.db.query(
                func.date_trunc('week', ActivityLog.date).label('week'),
                func.count(ActivityLog.id).label('count')
            ).filter(
                and_(
                    ActivityLog.user_id == uuid_id,
                    ActivityLog.date >= start_date,
                    ActivityLog.date <= end_date
                )
            ).group_by(
                func.date_trunc('week', ActivityLog.date)
            ).order_by('week').all()
            
            # Format weekly data
            weekly_trends = [
                {
                    "week": week.isoformat() if week else None,
                    "count": count
                }
                for week, count in weekly_data
            ]
            
            # Calculate trend direction
            if len(weekly_trends) >= 2:
                recent_avg = sum(w['count'] for w in weekly_trends[-2:]) / 2
                older_avg = sum(w['count'] for w in weekly_trends[:2]) / 2
                trend_direction = "increasing" if recent_avg > older_avg else "decreasing"
            else:
                trend_direction = "stable"
            
            return {
                "period_days": days,
                "weekly_trends": weekly_trends,
                "trend_direction": trend_direction,
                "total_weeks": len(weekly_trends)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting activity trends: {e}")
            return {}
    
    def search_activities(self, user_id: str, search_term: str, limit: int = 20) -> List[ActivityLog]:
        """
        Search activities by content or notes.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            
            # Search in activities JSONB field and notes
            activities = self.db.query(ActivityLog).filter(
                and_(
                    ActivityLog.user_id == uuid_id,
                    func.lower(func.cast(ActivityLog.activities, db.String)).contains(search_term.lower()) |
                    func.lower(ActivityLog.notes).contains(search_term.lower())
                )
            ).order_by(desc(ActivityLog.date)).limit(limit).all()
            
            return activities
            
        except Exception as e:
            self.logger.error(f"Error searching activities: {e}")
            return []
