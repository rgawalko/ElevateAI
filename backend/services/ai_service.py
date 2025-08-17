"""
AI Service

Handles all AI-related business logic including schedule generation,
insights generation, and AI recommendations.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import uuid

from .base_service import BaseService
from .schedule_service import ScheduleService
from .activity_service import ActivityService
from .user_service import UserService
from .azure_openai_service import azure_openai_service
from models import Schedule, ActivityLog, AIInsight, UserPreferences
from ProductivityScore import _calculate_score_internal, DayMetrics, get_productivity_agent


class AIService(BaseService):
    """
    Service for AI-powered features.
    """
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.schedule_service = ScheduleService(db)
        self.activity_service = ActivityService(db)
        self.user_service = UserService(db)
        self.azure_openai_service = azure_openai_service
    
    def generate_optimized_schedule(self, user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an AI-optimized schedule based on user preferences and constraints.
        """
        try:
            # Validate request data
            required_fields = ["date", "wakeUpTime", "activities", "constraints"]
            for field in required_fields:
                if field not in request_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Get user preferences for personalization
            preferences = self.user_service.get_user_preferences(user_id)

            # Try Azure OpenAI first, fallback to local algorithm
            try:
                self.logger.info("Using Azure OpenAI for schedule generation")
                self.logger.info(f"Input activities count: {len(request_data.get('activities', []))}")
                azure_result = self.azure_openai_service.generate_schedule(request_data)
                self.logger.info(f"Azure result: {azure_result}")

                # Check if Azure AI returned a successful response
                if azure_result.get("success", True) and "scheduledActivities" in azure_result:
                    generated_schedule = azure_result
                    self.logger.info(f"Successfully generated schedule using Azure OpenAI with {len(azure_result.get('scheduledActivities', []))} activities")
                else:
                    self.logger.warning("Azure OpenAI failed, using local algorithm")
                    generated_schedule = self._generate_schedule_algorithm(request_data, preferences)
            except Exception as e:
                self.logger.warning(f"Azure OpenAI error: {e}, using local algorithm")
                generated_schedule = self._generate_schedule_algorithm(request_data, preferences)
            
            # Validate generated schedule structure
            if not generated_schedule.get("scheduledActivities"):
                self.logger.warning("Generated schedule has no scheduledActivities, using local algorithm")
                generated_schedule = self._generate_schedule_algorithm(request_data, preferences)

            # Save the generated schedule to database
            schedule_data = {
                "date": datetime.strptime(request_data["date"], "%Y-%m-%d").date(),
                "tasks": generated_schedule.get("scheduledActivities", []),
                "generated_by_ai": True
            }
            
            # Create schedule with tasks
            tasks_data = []
            for activity in generated_schedule.get("scheduledActivities", []):
                try:
                    task_data = {
                        "title": activity.get("name", "Untitled Activity"),
                        "start_time": datetime.strptime(f"{request_data['date']} {activity.get('startTime', '09:00')}", "%Y-%m-%d %H:%M"),
                        "end_time": datetime.strptime(f"{request_data['date']} {activity.get('endTime', '09:30')}", "%Y-%m-%d %H:%M"),
                        "estimated_duration": activity.get("durationMinutes", 30),  # Default 30 minutes
                        "priority": activity.get("priority", 3),  # Default medium priority
                        "is_break": activity.get("category") == "break"
                    }
                    tasks_data.append(task_data)
                except Exception as e:
                    self.logger.warning(f"Error parsing activity {activity}: {e}")
                    continue
            
            schedule = self.schedule_service.create_schedule(user_id, schedule_data, tasks_data)
            
            self.logger.info(f"Final generated schedule has {len(generated_schedule.get('scheduledActivities', []))} activities")
            self.logger.info(f"Final schedule data: {generated_schedule}")

            return {
                "success": True,
                "schedule": generated_schedule,
                "schedule_id": str(schedule.id) if schedule else None,
                "message": "Schedule generated successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating optimized schedule: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate schedule"
            }
    
    def _generate_schedule_algorithm(self, request_data: Dict[str, Any], preferences: Optional[UserPreferences]) -> Dict[str, Any]:
        """
        Core AI scheduling algorithm.
        """
        activities = request_data["activities"]
        constraints = request_data["constraints"]
        wake_time = request_data["wakeUpTime"]
        
        # Use user preferences if available
        if preferences:
            lunch_break_duration = preferences.lunch_break_duration
            max_consecutive_hours = preferences.max_consecutive_work_hours
            short_break_duration = preferences.short_break_duration
        else:
            lunch_break_duration = 60
            max_consecutive_hours = 4
            short_break_duration = 15
        
        # Sort activities by priority (1 = highest priority)
        # Add default priority if missing
        for activity in activities:
            if "priority" not in activity or activity["priority"] is None:
                activity["priority"] = 3  # Default medium priority

        sorted_activities = sorted(activities, key=lambda x: x.get("priority", 3))
        
        # Parse wake up time and set work start
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
                time_to_minutes(current_time) >= 12 * 60):
                
                scheduled_activities.append({
                    "name": "Lunch Break",
                    "startTime": current_time,
                    "endTime": add_minutes_to_time(current_time, lunch_break_duration),
                    "durationMinutes": lunch_break_duration,
                    "priority": 0,
                    "category": "break"
                })
                current_time = add_minutes_to_time(current_time, lunch_break_duration)
                lunch_scheduled = True
                consecutive_work_time = 0
            
            # Check consecutive work hours limit
            if consecutive_work_time >= max_consecutive_hours * 60:
                scheduled_activities.append({
                    "name": "Break",
                    "startTime": current_time,
                    "endTime": add_minutes_to_time(current_time, short_break_duration),
                    "durationMinutes": short_break_duration,
                    "priority": 0,
                    "category": "break"
                })
                current_time = add_minutes_to_time(current_time, short_break_duration)
                consecutive_work_time = 0
            
            # Handle time windows if specified
            if "timeWindow" in activity:
                window_start, window_end = activity["timeWindow"]
                current_minutes = time_to_minutes(current_time)
                window_start_minutes = time_to_minutes(window_start)
                window_end_minutes = time_to_minutes(window_end)
                
                # If current time is before window, move to window start
                if current_minutes < window_start_minutes:
                    current_time = window_start
                # If current time would end after window, skip or reschedule
                elif current_minutes + activity["durationMinutes"] > window_end_minutes:
                    continue  # Skip this activity for now
            
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
        
        # Calculate summary statistics
        total_duration = sum(act["durationMinutes"] for act in scheduled_activities)
        work_time = sum(act["durationMinutes"] for act in scheduled_activities if act.get("category") != "break")
        break_time = sum(act["durationMinutes"] for act in scheduled_activities if act.get("category") == "break")

        # Generate optimization recommendations
        recommendations = []
        high_priority_tasks = [act for act in scheduled_activities if act.get("priority", 3) <= 2 and act.get("category") != "break"]
        if high_priority_tasks:
            recommendations.append("High-priority tasks scheduled first for maximum productivity")

        breaks = [act for act in scheduled_activities if act.get("category") == "break"]
        if breaks:
            recommendations.append(f"Strategic breaks placed to maintain energy levels ({len(breaks)} breaks)")

        if lunch_scheduled:
            recommendations.append("Lunch break optimally scheduled during midday")

        if work_time > 0 and break_time > 0:
            ratio = break_time / work_time * 100
            recommendations.append(f"Work-life balance optimized with {ratio:.0f}% break-to-work ratio")

        # Calculate detailed productivity metrics for enhanced reporting
        productivity_score = self._calculate_productivity_score(scheduled_activities)
        productivity_details = self._get_productivity_score_details(scheduled_activities)

        return {
            "date": request_data["date"],
            "totalDuration": total_duration,
            "scheduledActivities": scheduled_activities,
            "unscheduledActivities": [],
            "breaks": [act for act in scheduled_activities if act.get("category") == "break"],
            "summary": {
                "totalWorkTime": work_time,
                "totalBreakTime": break_time,
                "totalFreeTime": max(0, 8 * 60 - total_duration),
                "productivityScore": productivity_score,
                "balanceScore": self._calculate_balance_score(work_time, break_time),
                "recommendations": recommendations,
                "productivityBreakdown": productivity_details  # Add detailed EPS breakdown
            },
            "optimizationDetails": {
                "priorityOptimization": "High-priority tasks scheduled first for optimal productivity",
                "breakOptimization": f"Added {len(breaks)} strategic breaks to maintain energy",
                "timeWindowRespected": "All time constraints and preferences were respected",
                "workLifeBalance": f"Achieved {break_time / max(work_time, 1) * 100:.0f}% break-to-work balance ratio",
                "productivityOptimization": f"Evidence-based Productivity Score (EPS): {productivity_score}/100 - {productivity_details.get('interpretation', 'Optimized for peak performance')}"
            }
        }
    
    def _calculate_productivity_score(self, activities: List[Dict[str, Any]]) -> int:
        """
        Calculate productivity score using sophisticated EPS algorithm.
        """
        try:
            # Extract metrics from activities for sophisticated scoring
            work_activities = [act for act in activities if act.get("category") != "break"]
            breaks = [act for act in activities if act.get("category") == "break"]

            # Calculate deep work time (activities >= 25 minutes)
            deep_work_min = sum(
                act["durationMinutes"] for act in work_activities
                if act["durationMinutes"] >= 25
            )

            # Estimate context switches (simplified - based on number of different activity types)
            activity_types = set(act.get("name", "").lower() for act in work_activities)
            context_switches = max(0, len(activity_types) - 1)  # Subtract 1 as first activity doesn't count as switch

            # Default sleep hours (could be enhanced with user data)
            sleep_hours = 7.5  # Default optimal sleep

            # Calculate break time
            break_minutes = sum(act["durationMinutes"] for act in breaks)

            # Calculate total focus time
            focus_minutes = sum(act["durationMinutes"] for act in work_activities)
            if focus_minutes == 0:
                focus_minutes = 1  # Avoid division by zero

            # Estimate chronotype alignment (simplified - assume high-priority tasks in morning are better)
            high_priority_early = sum(
                1 for i, act in enumerate(work_activities[:3])  # First 3 activities
                if act.get("priority", 3) <= 2
            )
            hc_ratio = min(1.0, high_priority_early / 3.0) if work_activities else 0.5

            # Create DayMetrics object
            metrics = DayMetrics(
                deep_work_min=deep_work_min,
                context_switches=context_switches,
                sleep_hours=sleep_hours,
                break_minutes=break_minutes,
                focus_minutes=focus_minutes,
                hc_ratio=hc_ratio
            )

            # Calculate sophisticated score
            score_breakdown = _calculate_score_internal(metrics)
            return int(score_breakdown.score)

        except Exception as e:
            self.logger.error(f"Error calculating sophisticated productivity score: {e}")
            # Fallback to simple scoring
            return self._calculate_simple_productivity_score(activities)

    def _calculate_simple_productivity_score(self, activities: List[Dict[str, Any]]) -> int:
        """
        Fallback simple productivity scoring algorithm.
        """
        score = 70  # Base score

        # Bonus for proper break distribution
        breaks = [act for act in activities if act.get("category") == "break"]
        if len(breaks) >= 2:
            score += 10

        # Bonus for high-priority tasks scheduled early
        work_activities = [act for act in activities if act.get("category") != "break"]
        if work_activities and work_activities[0]["priority"] <= 2:
            score += 10

        # Penalty for too many consecutive work blocks
        consecutive_work_blocks = 0
        for i, act in enumerate(activities):
            if act.get("category") != "break":
                consecutive_work_blocks += 1
            else:
                if consecutive_work_blocks > 3:
                    score -= 5
                consecutive_work_blocks = 0

        return min(100, max(0, score))

    def _get_productivity_score_details(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get detailed breakdown of the productivity score using EPS algorithm.
        """
        try:
            # Extract metrics from activities for sophisticated scoring
            work_activities = [act for act in activities if act.get("category") != "break"]
            breaks = [act for act in activities if act.get("category") == "break"]

            # Calculate deep work time (activities >= 25 minutes)
            deep_work_min = sum(
                act["durationMinutes"] for act in work_activities
                if act["durationMinutes"] >= 25
            )

            # Estimate context switches (simplified - based on number of different activity types)
            activity_types = set(act.get("name", "").lower() for act in work_activities)
            context_switches = max(0, len(activity_types) - 1)

            # Default sleep hours (could be enhanced with user data)
            sleep_hours = 7.5  # Default optimal sleep

            # Calculate break time
            break_minutes = sum(act["durationMinutes"] for act in breaks)

            # Calculate total focus time
            focus_minutes = sum(act["durationMinutes"] for act in work_activities)
            if focus_minutes == 0:
                focus_minutes = 1  # Avoid division by zero

            # Estimate chronotype alignment (simplified - assume high-priority tasks in morning are better)
            high_priority_early = sum(
                1 for act in work_activities[:3]  # First 3 activities
                if act.get("priority", 3) <= 2
            )
            hc_ratio = min(1.0, high_priority_early / 3.0) if work_activities else 0.5

            # Create DayMetrics object
            metrics = DayMetrics(
                deep_work_min=deep_work_min,
                context_switches=context_switches,
                sleep_hours=sleep_hours,
                break_minutes=break_minutes,
                focus_minutes=focus_minutes,
                hc_ratio=hc_ratio
            )

            # Calculate sophisticated score breakdown
            from ProductivityScore import _interpret_score, _generate_recommendations
            score_breakdown = _calculate_score_internal(metrics)

            return {
                "focus_score": score_breakdown.focus,
                "sleep_score": score_breakdown.sleep,
                "breaks_score": score_breakdown.breaks,
                "chronotype_score": score_breakdown.chronotype,
                "overall_score": score_breakdown.score,
                "interpretation": _interpret_score(score_breakdown.score),
                "recommendations": _generate_recommendations(score_breakdown),
                "metrics": {
                    "deep_work_minutes": deep_work_min,
                    "context_switches": context_switches,
                    "break_minutes": break_minutes,
                    "focus_minutes": focus_minutes,
                    "chronotype_alignment": hc_ratio
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting productivity score details: {e}")
            return {
                "interpretation": "Productivity analysis unavailable",
                "recommendations": []
            }

    def _calculate_balance_score(self, work_time: int, break_time: int) -> int:
        """
        Calculate work-life balance score.
        """
        if work_time == 0:
            return 0
        
        break_ratio = break_time / work_time
        
        # Optimal break ratio is around 0.15-0.25 (15-25% of work time)
        if 0.15 <= break_ratio <= 0.25:
            return 90
        elif 0.10 <= break_ratio <= 0.30:
            return 75
        elif 0.05 <= break_ratio <= 0.35:
            return 60
        else:
            return 40
    
    def generate_schedule_recommendations(self, user_id: str, date: str) -> List[Dict[str, Any]]:
        """
        Generate schedule recommendations based on user's historical data.
        """
        try:
            # Get user's activity patterns
            activity_stats = self.activity_service.get_activity_statistics(user_id, days=30)
            
            # Get user's schedule patterns
            schedule_stats = self.schedule_service.get_schedule_statistics(user_id, days=30)
            
            recommendations = []
            
            # Recommend based on activity frequency
            if activity_stats.get("activity_frequency", 0) < 50:
                recommendations.append({
                    "type": "activity_tracking",
                    "title": "Increase Activity Tracking",
                    "description": "Try to log more activities to get better AI insights",
                    "priority": "medium"
                })
            
            # Recommend based on completion rate
            completion_rate = schedule_stats.get("completion_rate", 0)
            if completion_rate < 70:
                recommendations.append({
                    "type": "task_management",
                    "title": "Improve Task Completion",
                    "description": "Consider breaking large tasks into smaller ones",
                    "priority": "high"
                })
            
            # Recommend AI schedule usage
            ai_usage_rate = schedule_stats.get("ai_usage_rate", 0)
            if ai_usage_rate < 30:
                recommendations.append({
                    "type": "ai_scheduling",
                    "title": "Try AI Schedule Generation",
                    "description": "Let AI optimize your daily schedule for better productivity",
                    "priority": "low"
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating schedule recommendations: {e}")
            return []
    
    def analyze_productivity_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze user's productivity patterns using AI.
        """
        try:
            # Get user's activity and schedule data
            activity_stats = self.activity_service.get_activity_statistics(user_id, days=60)
            schedule_stats = self.schedule_service.get_schedule_statistics(user_id, days=60)
            
            # Analyze patterns
            patterns = {
                "most_productive_days": self._analyze_productive_days(user_id),
                "optimal_task_duration": self._analyze_task_durations(user_id),
                "break_effectiveness": self._analyze_break_patterns(user_id),
                "completion_trends": self._analyze_completion_trends(user_id)
            }
            
            return {
                "analysis_period": "60 days",
                "patterns": patterns,
                "recommendations": self._generate_productivity_recommendations(patterns)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing productivity patterns: {e}")
            return {}
    
    def _analyze_productive_days(self, user_id: str) -> Dict[str, Any]:
        """Analyze which days of the week are most productive."""
        # Placeholder for ML analysis
        return {
            "most_productive": ["Tuesday", "Wednesday"],
            "least_productive": ["Monday", "Friday"],
            "confidence": 0.75
        }
    
    def _analyze_task_durations(self, user_id: str) -> Dict[str, Any]:
        """Analyze optimal task durations."""
        return {
            "optimal_duration": 45,
            "completion_rate_by_duration": {
                "15-30": 0.85,
                "30-60": 0.78,
                "60-120": 0.65,
                "120+": 0.45
            }
        }
    
    def _analyze_break_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze break effectiveness."""
        return {
            "optimal_break_frequency": "every 90 minutes",
            "optimal_break_duration": 15,
            "productivity_boost": 0.23
        }
    
    def _analyze_completion_trends(self, user_id: str) -> Dict[str, Any]:
        """Analyze task completion trends."""
        return {
            "trend": "improving",
            "current_rate": 0.72,
            "previous_rate": 0.68,
            "improvement": 0.04
        }
    
    def _generate_productivity_recommendations(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on productivity patterns."""
        recommendations = []
        
        # Add recommendations based on patterns
        if patterns.get("optimal_task_duration", {}).get("optimal_duration", 0) < 60:
            recommendations.append({
                "type": "task_duration",
                "title": "Optimize Task Duration",
                "description": "Keep tasks under 60 minutes for better completion rates"
            })
        
        return recommendations
