"""
Schedule Service

Handles all schedule-related business logic including schedule management,
task tracking, and AI schedule generation.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta, date
import uuid

from .base_service import BaseService
from models import Schedule, ScheduleTask


class ScheduleService(BaseService):
    """
    Service for schedule management operations.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    def create_schedule(self, user_id: str, schedule_data: Dict[str, Any], tasks: List[Dict[str, Any]] = None) -> Optional[Schedule]:
        """
        Create a new schedule with optional tasks.
        """
        try:
            # Prepare schedule data
            schedule_data['user_id'] = uuid.UUID(user_id)
            
            # Create schedule
            schedule = Schedule(**schedule_data)
            self.db.add(schedule)
            self.db.flush()  # Get schedule ID
            
            # Create tasks if provided
            if tasks:
                for task_data in tasks:
                    task_data['schedule_id'] = schedule.id
                    task_data['user_id'] = uuid.UUID(user_id)
                    task = ScheduleTask(**task_data)
                    self.db.add(task)
            
            self.db.commit()
            self.db.refresh(schedule)
            
            self.logger.info(f"Created schedule for user {user_id} with {len(tasks or [])} tasks")
            return schedule
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating schedule: {e}")
            return None
    
    def get_user_schedules(self, user_id: str, filters: Dict[str, Any] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Get user's schedules with filtering and pagination.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            query = self.db.query(Schedule).options(
                joinedload(Schedule.schedule_tasks)
            ).filter(Schedule.user_id == uuid_id)
            
            # Apply filters
            if filters:
                if 'start_date' in filters and filters['start_date']:
                    query = query.filter(Schedule.date >= filters['start_date'])
                
                if 'end_date' in filters and filters['end_date']:
                    query = query.filter(Schedule.date <= filters['end_date'])
                
                if 'ai_generated' in filters and filters['ai_generated'] is not None:
                    query = query.filter(Schedule.generated_by_ai == filters['ai_generated'])
            
            # Order by date descending
            query = query.order_by(desc(Schedule.date))
            
            return self.paginate(query, page, per_page)
            
        except Exception as e:
            self.logger.error(f"Error getting user schedules: {e}")
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "pages": 0}
    
    def get_schedule_with_tasks(self, schedule_id: str, user_id: str) -> Optional[Schedule]:
        """
        Get schedule with tasks loaded.
        """
        try:
            uuid_schedule_id = uuid.UUID(schedule_id)
            uuid_user_id = uuid.UUID(user_id)
            
            return self.db.query(Schedule).options(
                joinedload(Schedule.schedule_tasks)
            ).filter(
                and_(
                    Schedule.id == uuid_schedule_id,
                    Schedule.user_id == uuid_user_id
                )
            ).first()
            
        except Exception as e:
            self.logger.error(f"Error getting schedule with tasks: {e}")
            return None
    
    def update_schedule(self, schedule_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Schedule]:
        """
        Update schedule information.
        """
        try:
            schedule = self.get_schedule_with_tasks(schedule_id, user_id)
            if not schedule:
                return None
            
            # Update schedule fields
            for field, value in update_data.items():
                if hasattr(schedule, field) and field not in ['id', 'user_id', 'created_at']:
                    setattr(schedule, field, value)
            
            self.db.commit()
            self.db.refresh(schedule)
            return schedule
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating schedule: {e}")
            return None
    
    def delete_schedule(self, schedule_id: str, user_id: str) -> bool:
        """
        Delete schedule and all associated tasks.
        """
        try:
            schedule = self.get_schedule_with_tasks(schedule_id, user_id)
            if not schedule:
                return False
            
            return self.delete(schedule)
            
        except Exception as e:
            self.logger.error(f"Error deleting schedule: {e}")
            return False
    
    def create_schedule_task(self, schedule_id: str, user_id: str, task_data: Dict[str, Any]) -> Optional[ScheduleTask]:
        """
        Create a new task within a schedule.
        """
        try:
            # Verify schedule belongs to user
            schedule = self.get_schedule_with_tasks(schedule_id, user_id)
            if not schedule:
                return None
            
            # Prepare task data
            task_data['schedule_id'] = uuid.UUID(schedule_id)
            task_data['user_id'] = uuid.UUID(user_id)
            
            task = ScheduleTask(**task_data)
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            return task
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating schedule task: {e}")
            return None
    
    def update_schedule_task(self, task_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[ScheduleTask]:
        """
        Update schedule task.
        """
        try:
            uuid_task_id = uuid.UUID(task_id)
            uuid_user_id = uuid.UUID(user_id)
            
            task = self.db.query(ScheduleTask).filter(
                and_(
                    ScheduleTask.id == uuid_task_id,
                    ScheduleTask.user_id == uuid_user_id
                )
            ).first()
            
            if not task:
                return None
            
            return self.update(task, update_data)
            
        except Exception as e:
            self.logger.error(f"Error updating schedule task: {e}")
            return None
    
    def complete_schedule_task(self, task_id: str, user_id: str, notes: str = None, actual_duration: int = None) -> Optional[ScheduleTask]:
        """
        Mark a schedule task as completed.
        """
        try:
            uuid_task_id = uuid.UUID(task_id)
            uuid_user_id = uuid.UUID(user_id)
            
            task = self.db.query(ScheduleTask).filter(
                and_(
                    ScheduleTask.id == uuid_task_id,
                    ScheduleTask.user_id == uuid_user_id
                )
            ).first()
            
            if not task:
                return None
            
            task.mark_completed(notes, actual_duration)
            self.db.commit()
            self.db.refresh(task)
            
            return task
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error completing schedule task: {e}")
            return None
    
    def get_schedule_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get schedule statistics for the specified number of days.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            end_date = datetime.now(timezone.utc).date()
            start_date = end_date - timedelta(days=days)
            
            # Get schedules in date range
            schedules = self.db.query(Schedule).filter(
                and_(
                    Schedule.user_id == uuid_id,
                    Schedule.date >= start_date,
                    Schedule.date <= end_date
                )
            ).all()
            
            # Get tasks in date range
            tasks = self.db.query(ScheduleTask).filter(
                and_(
                    ScheduleTask.user_id == uuid_id,
                    ScheduleTask.start_time >= datetime.combine(start_date, datetime.min.time()),
                    ScheduleTask.start_time <= datetime.combine(end_date, datetime.max.time())
                )
            ).all()
            
            # Calculate statistics
            total_schedules = len(schedules)
            ai_generated_schedules = len([s for s in schedules if s.generated_by_ai])
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.is_completed])
            
            # Calculate completion rate
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Calculate average tasks per schedule
            avg_tasks_per_schedule = total_tasks / max(total_schedules, 1)
            
            # Get overdue tasks
            overdue_tasks = len([t for t in tasks if t.is_overdue])
            
            return {
                "period_days": days,
                "total_schedules": total_schedules,
                "ai_generated_schedules": ai_generated_schedules,
                "ai_usage_rate": (ai_generated_schedules / total_schedules * 100) if total_schedules > 0 else 0,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "completion_rate": round(completion_rate, 1),
                "average_tasks_per_schedule": round(avg_tasks_per_schedule, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting schedule statistics: {e}")
            return {}
    
    def get_today_schedule(self, user_id: str) -> Optional[Schedule]:
        """
        Get today's schedule for a user.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            today = datetime.now(timezone.utc).date()
            
            return self.db.query(Schedule).options(
                joinedload(Schedule.schedule_tasks)
            ).filter(
                and_(
                    Schedule.user_id == uuid_id,
                    Schedule.date == today
                )
            ).first()
            
        except Exception as e:
            self.logger.error(f"Error getting today's schedule: {e}")
            return None
    
    def get_upcoming_tasks(self, user_id: str, hours: int = 24) -> List[ScheduleTask]:
        """
        Get upcoming tasks within the specified number of hours.
        """
        try:
            uuid_id = uuid.UUID(user_id)
            now = datetime.now(timezone.utc)
            end_time = now + timedelta(hours=hours)
            
            tasks = self.db.query(ScheduleTask).filter(
                and_(
                    ScheduleTask.user_id == uuid_id,
                    ScheduleTask.start_time >= now,
                    ScheduleTask.start_time <= end_time,
                    ScheduleTask.is_completed == False
                )
            ).order_by(ScheduleTask.start_time).all()
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming tasks: {e}")
            return []
