"""
Home Page Service

Provides data aggregation and insights for the dashboard home page.
Retrieves user activities, statistics, and personalized recommendations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models.user import User
from models.activity_log import ActivityLog
from models.goal import Goal
from database.database import SessionLocal
from ProductivityScore import _calculate_score_internal, DayMetrics

logger = logging.getLogger(__name__)

class HomePageService:
    """Service for aggregating home page dashboard data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a user
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Dictionary containing all dashboard data
        """
        try:
            logger.info(f"Fetching dashboard data for user: {user_id}")
            
            # Get user info
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User not found: {user_id}")
                return self._get_default_dashboard_data()
            
            # Get date ranges
            today = datetime.now().date()
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)
            
            # Aggregate all data
            dashboard_data = {
                "user": {
                    "name": user.name,
                    "email": user.email,
                    "timezone": getattr(user, 'timezone', 'UTC')
                },
                "stats": self._get_user_stats(user_id, today, week_start, month_start),
                "recent_activities": self._get_recent_activities(user_id, limit=5),
                "today_schedule": self._get_today_schedule(user_id, today),
                "mood_energy": self._get_mood_energy_data(user_id, week_start),
                "goals_progress": self._get_goals_progress(user_id),
                "ai_insights": self._get_ai_insights(user_id, week_start),
                "productivity_trends": self._get_productivity_trends(user_id, week_start)
            }
            
            logger.info(f"Successfully fetched dashboard data for user: {user_id}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error fetching dashboard data for user {user_id}: {e}")
            return self._get_default_dashboard_data()
    
    def _get_user_stats(self, user_id: str, today: datetime.date,
                       week_start: datetime.date, month_start: datetime.date) -> Dict[str, Any]:
        """Get user statistics for different time periods"""

        # Today's activities
        today_activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            func.date(ActivityLog.date) == today
        ).count()

        # This week's activities
        week_activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            func.date(ActivityLog.date) >= week_start
        ).count()

        # Calculate average mood and energy from activity data
        # Since mood/energy are stored in the activities JSON field
        avg_mood = self._calculate_avg_mood(user_id, week_start)
        avg_energy = self._calculate_avg_energy(user_id, week_start)

        # Productivity score (calculated from activities and mood/energy)
        productivity_score = self._calculate_productivity_score(user_id, week_start)

        return {
            "activities_today": today_activities,
            "activities_this_week": week_activities,
            "time_tracked_today": self._calculate_time_tracked_today(user_id, today),
            "avg_mood": avg_mood,
            "avg_energy": avg_energy,
            "productivity_score": productivity_score
        }
    
    def _get_recent_activities(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get user's most recent activities"""

        activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).order_by(desc(ActivityLog.date)).limit(limit).all()

        result = []
        for activity in activities:
            # Parse activities from JSON field
            activities_data = activity.activities or []
            if isinstance(activities_data, list) and activities_data:
                # Get the first activity from the day
                activity_data = activities_data[0] if activities_data else {}
                result.append({
                    "id": str(activity.id),
                    "title": activity_data.get("title", "Activity"),
                    "category": activity_data.get("category", "general"),
                    "duration": activity_data.get("duration", 0),
                    "start_time": activity.date.isoformat(),
                    "mood": activity_data.get("mood", None),
                    "energy_level": activity_data.get("energy_level", None)
                })

        return result

    def _calculate_time_tracked_today(self, user_id: str, today: datetime.date) -> int:
        """Calculate total time tracked today from activity logs"""
        activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            func.date(ActivityLog.date) == today
        ).all()

        total_time = 0
        for activity in activities:
            activities_data = activity.activities or []
            if isinstance(activities_data, list):
                for activity_data in activities_data:
                    total_time += activity_data.get("duration", 0)

        return total_time

    def _calculate_avg_mood(self, user_id: str, week_start: datetime.date) -> float:
        """Calculate average mood from activity logs"""
        activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            func.date(ActivityLog.date) >= week_start
        ).all()

        moods = []
        for activity in activities:
            activities_data = activity.activities or []
            if isinstance(activities_data, list):
                for activity_data in activities_data:
                    mood = activity_data.get("mood")
                    if mood is not None:
                        moods.append(mood)

        return round(sum(moods) / len(moods), 1) if moods else 0

    def _calculate_avg_energy(self, user_id: str, week_start: datetime.date) -> float:
        """Calculate average energy from activity logs"""
        activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            func.date(ActivityLog.date) >= week_start
        ).all()

        energy_levels = []
        for activity in activities:
            activities_data = activity.activities or []
            if isinstance(activities_data, list):
                for activity_data in activities_data:
                    energy = activity_data.get("energy_level")
                    if energy is not None:
                        energy_levels.append(energy)

        return round(sum(energy_levels) / len(energy_levels), 1) if energy_levels else 0
    
    def _get_today_schedule(self, user_id: str, today: datetime.date) -> List[Dict[str, Any]]:
        """Get today's scheduled activities/tasks"""

        # For now, return sample scheduled tasks since we don't have a separate schedule table
        # In a real implementation, this would query from a Schedule/Task table
        return [
            {
                "id": "1",
                "title": "Morning Review",
                "time": "09:00",
                "category": "work",
                "duration": 30
            },
            {
                "id": "2",
                "title": "Team Meeting",
                "time": "14:00",
                "category": "work",
                "duration": 60
            }
        ]
    
    def _get_mood_energy_data(self, user_id: str, week_start: datetime.date) -> Dict[str, Any]:
        """Get mood and energy trends for the week"""

        # Get activity logs for the past week and extract mood/energy data
        activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            func.date(ActivityLog.date) >= week_start
        ).all()

        # Group by date and calculate averages
        daily_data = {}
        for activity in activities:
            date_str = str(activity.date.date())
            if date_str not in daily_data:
                daily_data[date_str] = {"moods": [], "energies": []}

            activities_data = activity.activities or []
            if isinstance(activities_data, list):
                for activity_data in activities_data:
                    mood = activity_data.get("mood")
                    energy = activity_data.get("energy_level")
                    if mood is not None:
                        daily_data[date_str]["moods"].append(mood)
                    if energy is not None:
                        daily_data[date_str]["energies"].append(energy)

        # Calculate daily averages
        mood_trend = []
        energy_trend = []

        for date_str, data in daily_data.items():
            if data["moods"]:
                avg_mood = sum(data["moods"]) / len(data["moods"])
                mood_trend.append({"date": date_str, "value": round(avg_mood, 1)})

            if data["energies"]:
                avg_energy = sum(data["energies"]) / len(data["energies"])
                energy_trend.append({"date": date_str, "value": round(avg_energy, 1)})

        return {
            "mood_trend": mood_trend,
            "energy_trend": energy_trend
        }
    
    def _get_goals_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's goals and their progress"""
        
        goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.is_active == True,
            Goal.is_completed == False
        ).limit(3).all()

        total_goals = self.db.query(Goal).filter(Goal.user_id == user_id).count()
        completed_goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.is_completed == True
        ).count()
        
        return {
            "active_goals": [
                {
                    "id": str(goal.id),
                    "title": goal.title,
                    "progress": round((goal.current_value / goal.target_value * 100), 1) if goal.target_value > 0 else 0,
                    "target_date": goal.deadline.isoformat() if goal.deadline else None,
                    "category": goal.category
                }
                for goal in goals
            ],
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "completion_rate": round((completed_goals / total_goals * 100), 1) if total_goals > 0 else 0
        }
    
    def _get_ai_insights(self, user_id: str, week_start: datetime.date) -> List[Dict[str, Any]]:
        """Generate AI-powered insights based on user data"""
        
        # This would typically involve more complex analysis
        # For now, we'll provide some basic insights based on patterns
        
        insights = []
        
        # Productivity peak analysis
        peak_hours = self._analyze_productivity_peaks(user_id, week_start)
        if peak_hours:
            insights.append({
                "type": "productivity_peak",
                "title": "🎯 Productivity Peak",
                "description": f"Your most productive hours are between {peak_hours}. Consider scheduling important tasks during this time.",
                "priority": "high"
            })
        
        # Energy optimization
        energy_insight = self._analyze_energy_patterns(user_id, week_start)
        if energy_insight:
            insights.append({
                "type": "energy_optimization",
                "title": "💪 Energy Optimization",
                "description": energy_insight,
                "priority": "medium"
            })
        
        return insights
    
    def _calculate_productivity_score(self, user_id: str, week_start: datetime.date) -> float:
        """Calculate a sophisticated productivity score using EPS algorithm"""
        try:
            # Get activities for the week
            activities = self.db.query(ActivityLog).filter(
                ActivityLog.user_id == user_id,
                func.date(ActivityLog.date) >= week_start
            ).all()

            if not activities:
                return 5.0  # Default score when no data

            # Extract metrics from activities
            total_duration = sum(act.duration_minutes for act in activities if act.duration_minutes)

            # Calculate deep work time (activities >= 25 minutes)
            deep_work_min = sum(
                act.duration_minutes for act in activities
                if act.duration_minutes and act.duration_minutes >= 25
            )

            # Estimate context switches based on activity variety per day
            daily_activities = {}
            for act in activities:
                day = act.date.date() if hasattr(act.date, 'date') else act.date
                if day not in daily_activities:
                    daily_activities[day] = set()
                daily_activities[day].add(act.activity_name.lower())

            # Average context switches per day
            avg_context_switches = sum(
                max(0, len(day_acts) - 1) for day_acts in daily_activities.values()
            ) / max(1, len(daily_activities))

            # Use average mood and energy for sleep estimation
            avg_mood = self._calculate_avg_mood(user_id, week_start)
            avg_energy = self._calculate_avg_energy(user_id, week_start)

            # Estimate sleep quality from mood/energy (7.5 baseline, adjust based on mood/energy)
            sleep_hours = 7.5
            if avg_mood > 0 and avg_energy > 0:
                mood_energy_avg = (avg_mood + avg_energy) / 2
                # Scale mood/energy (1-10) to sleep adjustment (-1 to +1 hours)
                sleep_adjustment = (mood_energy_avg - 5.5) * 0.3
                sleep_hours = max(5.0, min(9.0, sleep_hours + sleep_adjustment))

            # Estimate break time (assume 10% of total time as breaks)
            break_minutes = int(total_duration * 0.1)

            # Focus time is total duration minus breaks
            focus_minutes = max(1, total_duration - break_minutes)

            # Estimate chronotype alignment (simplified - higher mood/energy suggests better alignment)
            hc_ratio = 0.5  # Default
            if avg_mood > 0 and avg_energy > 0:
                mood_energy_avg = (avg_mood + avg_energy) / 2
                hc_ratio = min(1.0, mood_energy_avg / 10.0)

            # Create DayMetrics object
            metrics = DayMetrics(
                deep_work_min=int(deep_work_min),
                context_switches=int(avg_context_switches),
                sleep_hours=sleep_hours,
                break_minutes=break_minutes,
                focus_minutes=focus_minutes,
                hc_ratio=hc_ratio
            )

            # Calculate sophisticated score
            score_breakdown = _calculate_score_internal(metrics)

            # Convert 0-100 scale to 0-10 scale for consistency with existing UI
            return round(score_breakdown.score / 10.0, 1)

        except Exception as e:
            logger.error(f"Error calculating sophisticated productivity score: {e}")
            # Fallback to simple calculation
            return self._calculate_simple_productivity_score(user_id, week_start)

    def _calculate_simple_productivity_score(self, user_id: str, week_start: datetime.date) -> float:
        """Fallback simple productivity calculation"""
        # Use the helper methods to get averages
        avg_mood = self._calculate_avg_mood(user_id, week_start)
        avg_energy = self._calculate_avg_energy(user_id, week_start)

        # Get activity completion rate (simplified)
        total_activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            func.date(ActivityLog.date) >= week_start
        ).count()

        # Simple productivity calculation (can be made more sophisticated)
        base_score = (avg_mood + avg_energy) / 2 if avg_mood > 0 and avg_energy > 0 else 5.0
        activity_bonus = min(total_activities * 0.1, 2.0)  # Cap at 2 points

        productivity_score = min(base_score + activity_bonus, 10.0)
        return round(productivity_score, 1)
    
    def _analyze_productivity_peaks(self, user_id: str, week_start: datetime.date) -> Optional[str]:
        """Analyze when user is most productive"""

        # For now, return a default peak time
        # In a real implementation, this would analyze activity timestamps and mood/energy data
        return "9:00-11:00"
    
    def _analyze_energy_patterns(self, user_id: str, week_start: datetime.date) -> Optional[str]:
        """Analyze energy patterns and provide recommendations"""

        # For now, return a default energy recommendation
        # In a real implementation, this would analyze energy patterns by time of day
        return "Taking a 15-minute walk after lunch could boost your afternoon energy levels by 20%."
    
    def _get_productivity_trends(self, user_id: str, week_start: datetime.date) -> Dict[str, Any]:
        """Get productivity trends over time"""

        # Get daily activity counts for the week from ActivityLog
        daily_activities = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id,
            func.date(ActivityLog.date) >= week_start
        ).all()

        # Process the data to get daily counts and time
        daily_data = {}
        for activity in daily_activities:
            date_str = str(activity.date.date())
            if date_str not in daily_data:
                daily_data[date_str] = {"count": 0, "total_time": 0}

            activities_data = activity.activities or []
            if isinstance(activities_data, list):
                daily_data[date_str]["count"] += len(activities_data)
                for activity_data in activities_data:
                    daily_data[date_str]["total_time"] += activity_data.get("duration", 0)

        return {
            "daily_activity_count": [
                {"date": date, "count": data["count"]}
                for date, data in daily_data.items()
            ],
            "daily_time_tracked": [
                {"date": date, "minutes": data["total_time"]}
                for date, data in daily_data.items()
            ]
        }
    
    def _get_default_dashboard_data(self) -> Dict[str, Any]:
        """Return default dashboard data when user data is unavailable"""
        
        return {
            "user": {"name": "User", "email": "", "timezone": "UTC"},
            "stats": {
                "activities_today": 0,
                "activities_this_week": 0,
                "time_tracked_today": 0,
                "avg_mood": 0,
                "avg_energy": 0,
                "productivity_score": 0
            },
            "recent_activities": [],
            "today_schedule": [],
            "mood_energy": {"mood_trend": [], "energy_trend": []},
            "goals_progress": {
                "active_goals": [],
                "total_goals": 0,
                "completed_goals": 0,
                "completion_rate": 0
            },
            "ai_insights": [],
            "productivity_trends": {
                "daily_activity_count": [],
                "daily_time_tracked": []
            }
        }


def get_home_page_service(db: Session = None) -> HomePageService:
    """Factory function to create HomePageService instance"""
    if db is None:
        db = SessionLocal()
    return HomePageService(db)
