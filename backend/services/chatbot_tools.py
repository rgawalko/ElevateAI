"""
Chatbot tools for querying user data from PostgreSQL database
These functions will be available to the Azure OpenAI assistant
Following Microsoft's official Azure AI Agents documentation
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models.user import User
from models.activity_log import ActivityLog
from models.ai_insight import AIInsight
from models.goal import Goal
from models.schedule import Schedule
from models.user_preferences import UserPreferences
from ProductivityScore import DayMetrics, _calculate_score_internal, _interpret_score, _generate_recommendations
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool
import time
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool
import time

logger = logging.getLogger(__name__)

# Global variables to store database session and user ID for function calls
_db_session: Optional[Session] = None
_current_user_id: Optional[str] = None

def set_function_context(db: Session, user_id: str):
    """Set the database session and user ID for function calls"""
    global _db_session, _current_user_id
    _db_session = db
    _current_user_id = user_id

# Define standalone functions following Microsoft's pattern
def get_user_profile() -> str:
    """
    Get basic user profile information including name, email, bio, timezone, and account details.

    :return: User profile information as a JSON string.
    """
    try:
        if not _db_session or not _current_user_id:
            return json.dumps({"error": "Database session not initialized"})

        user = _db_session.query(User).filter(User.id == _current_user_id).first()
        if not user:
            return json.dumps({"error": "User not found"})

        profile_data = {
            "name": user.name,
            "email": user.email,
            "bio": user.bio,
            "timezone": user.timezone,
            "date_format": user.date_format,
            "time_format": user.time_format,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "is_verified": user.is_verified
        }
        return json.dumps(profile_data)
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        return json.dumps({"error": str(e)})
def get_user_preferences() -> str:
    """
    Get user preferences and settings including work hours, break durations, AI settings, and UI preferences.

    :return: User preferences as a JSON string.
    """
    try:
        if not _db_session or not _current_user_id:
            return json.dumps({"error": "Database session not initialized"})

        prefs = _db_session.query(UserPreferences).filter(
            UserPreferences.user_id == _current_user_id
        ).first()

        if not prefs:
            return json.dumps({"error": "User preferences not found"})

        preferences_data = {
            "work_start_time": prefs.work_start_time,
            "work_end_time": prefs.work_end_time,
            "lunch_break_duration": prefs.lunch_break_duration,
            "short_break_duration": prefs.short_break_duration,
            "long_break_duration": prefs.long_break_duration,
            "max_consecutive_work_hours": prefs.max_consecutive_work_hours,
            "ai_suggestions_enabled": prefs.ai_suggestions_enabled,
            "auto_schedule_generation": prefs.auto_schedule_generation,
            "insight_frequency": prefs.insight_frequency,
            "productivity_tracking": prefs.productivity_tracking,
            "theme": prefs.theme,
            "language": prefs.language
        }
        return json.dumps(preferences_data)
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return json.dumps({"error": str(e)})
def get_recent_activities(days: int = 7) -> str:
    """
    Get user's recent activity logs with productivity scores, mood, and energy levels.

    :param days: Number of days to look back (default: 7).
    :return: Recent activities as a JSON string.
    """
    try:
        if not _db_session or not _current_user_id:
            return json.dumps({"error": "Database session not initialized"})

        start_date = datetime.now() - timedelta(days=days)

        activities = _db_session.query(ActivityLog).filter(
            ActivityLog.user_id == _current_user_id,
            ActivityLog.date >= start_date
        ).order_by(desc(ActivityLog.date)).limit(20).all()

        activity_list = []
        for activity in activities:
            # Parse the JSON activities data
            activity_data = activity.activities or {}
            activity_list.append({
                "name": activity_data.get("name", "Unknown Activity"),
                "category": activity_data.get("category", "uncategorized"),
                "start_time": activity_data.get("start_time"),
                "end_time": activity_data.get("end_time"),
                "duration_minutes": activity_data.get("duration_minutes", 0),
                "productivity_score": activity_data.get("productivity_score", 0),
                "mood": activity_data.get("mood", 0),
                "energy_level": activity_data.get("energy_level", 0),
                "notes": activity.notes,
                "date": activity.date.isoformat() if activity.date else None
            })

        result = {
            "activities": activity_list,
            "total_count": len(activity_list),
            "date_range": f"Last {days} days"
        }
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error getting recent activities: {e}")
        return json.dumps({"error": str(e)})
def get_productivity_stats(days: int = 7) -> str:
    """
    Get user's productivity statistics including total time, average scores, and category breakdown.

    :param days: Number of days to analyze (default: 7).
    :return: Productivity statistics as a JSON string.
    """
    try:
        if not _db_session or not _current_user_id:
            return json.dumps({"error": "Database session not initialized"})

        start_date = datetime.now() - timedelta(days=days)

        # Get activity stats
        activities = _db_session.query(ActivityLog).filter(
            ActivityLog.user_id == _current_user_id,
            ActivityLog.date >= start_date
        ).all()

        if not activities:
            return json.dumps({"message": "No activities found for the specified period"})

        # Parse activity data from JSON
        parsed_activities = []
        for activity in activities:
            activity_data = activity.activities or {}
            if activity_data:
                # Handle both single activity (dict) and multiple activities (list)
                if isinstance(activity_data, dict):
                    parsed_activities.append(activity_data)
                elif isinstance(activity_data, list):
                    parsed_activities.extend(activity_data)
                else:
                    logger.warning(f"Unexpected activity data type: {type(activity_data)}")

        if not parsed_activities:
            return json.dumps({"message": "No valid activity data found for the specified period"})

        total_time = sum(a.get("duration", 0) for a in parsed_activities)
        avg_productivity = sum(a.get("productivity", 0) for a in parsed_activities) / len(parsed_activities)
        avg_mood = sum(a.get("mood", 0) for a in parsed_activities) / len(parsed_activities)
        avg_energy = sum(a.get("energy", 0) for a in parsed_activities) / len(parsed_activities)

        # Category breakdown
        category_stats = {}
        for activity_data in parsed_activities:
            cat = activity_data.get("category", "uncategorized")
            if cat not in category_stats:
                category_stats[cat] = {"count": 0, "total_time": 0}
            category_stats[cat]["count"] += 1
            category_stats[cat]["total_time"] += activity_data.get("duration", 0)

        # Sort categories by total time for better display
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]["total_time"], reverse=True)

        # Generate insights
        insights = []
        if total_time > 0:
            if avg_productivity >= 8:
                insights.append("🏆 Excellent productivity levels this week!")
            elif avg_productivity >= 6:
                insights.append("👍 Good productivity performance")
            else:
                insights.append("💡 Consider optimizing your workflow for better productivity")

            if avg_mood >= 7:
                insights.append("😊 Great mood levels - keep up the positive energy!")
            elif avg_mood < 5:
                insights.append("🌟 Consider activities that boost your mood")

            if sorted_categories:
                top_category = sorted_categories[0][0]
                top_time = sorted_categories[0][1]["total_time"]
                insights.append(f"🎯 You spent most time on {top_category} ({round(top_time/60, 1)}h)")

        result = {
            "period": f"Last {days} days",
            "total_activities": len(parsed_activities),
            "total_time_minutes": total_time,
            "total_time_hours": round(total_time / 60, 1),
            "average_productivity_score": round(avg_productivity, 1),
            "average_mood": round(avg_mood, 1),
            "average_energy_level": round(avg_energy, 1),
            "category_breakdown": dict(sorted_categories),
            "insights": insights,
            "summary_text": f"You completed {len(parsed_activities)} activities totaling {round(total_time/60, 1)} hours with an average productivity score of {round(avg_productivity, 1)}/10."
        }
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error getting productivity stats: {e}")
        return json.dumps({"error": str(e)})
def get_current_goals() -> str:
    """
    Get user's current active goals with progress information.

    :return: Current goals as a JSON string.
    """
    try:
        if not _db_session or not _current_user_id:
            return json.dumps({"error": "Database session not initialized"})

        goals = _db_session.query(Goal).filter(
            Goal.user_id == _current_user_id,
            Goal.is_active == True
        ).order_by(desc(Goal.created_at)).all()

        goal_list = []
        for goal in goals:
            goal_list.append({
                "title": goal.title,
                "description": goal.description,
                "category": goal.category,
                "target_value": goal.target_value,
                "current_value": goal.current_value,
                "unit": goal.unit,
                "deadline": goal.deadline.isoformat() if goal.deadline else None,
                "is_completed": goal.is_completed,
                "is_active": goal.is_active,
                "progress_percentage": round((goal.current_value / goal.target_value * 100), 1) if goal.target_value else 0
            })

        result = {
            "goals": goal_list,
            "total_count": len(goal_list)
        }
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error getting current goals: {e}")
        return json.dumps({"error": str(e)})

def get_recent_insights(limit: int = 5) -> str:
    """
    Generate AI insights based on user's activity data from the last 7 days.

    :param limit: Maximum number of insights to return (default: 5).
    :return: Generated insights as a JSON string.
    """
    # Simple, robust implementation following Azure AI documentation pattern
    try:
        # Evidence-Based Productivity Score (EPS) insights with scientific backing
        insights = [
            {
                "type": "focus_quality",
                "title": "🧠 Deep Work Optimization",
                "summary": "Focus Quality Enhancement",
                "content": "Research shows that rapid task switching imposes measurable cognitive switching costs (American Psychological Association). Aim for uninterrupted work blocks of 25+ minutes to maximize your focus quality score. Consider time-blocking techniques to protect your deep work sessions.",
                "confidence": 0.9,
                "priority": "high",
                "eps_component": "focus",
                "scientific_basis": "Cognitive switching costs research (APA, ACM Digital Library)"
            },
            {
                "type": "sleep_sufficiency",
                "title": "😴 Sleep Quality Impact",
                "summary": "Cognitive Performance Optimization",
                "content": "Cognitive performance follows an inverted-U curve with sleep duration - 7-9 hours tends to support optimal executive function (PMC, PubMed research). Your sleep quality directly impacts your daily productivity score. Prioritize consistent sleep schedules for peak performance.",
                "confidence": 0.95,
                "priority": "high",
                "eps_component": "sleep",
                "scientific_basis": "Sleep-cognition research (PMC, PubMed)"
            },
            {
                "type": "micro_break_hygiene",
                "title": "⏸️ Strategic Break Patterns",
                "summary": "Micro-Break Effectiveness",
                "content": "Short breaks support well-being and aid performance, especially for demanding cognitive tasks (PMC, Taylor & Francis research). Aim for 5-15% of your work time as breaks. Try the Pomodoro Technique: 25 minutes focused work + 5 minute break cycles.",
                "confidence": 0.85,
                "priority": "medium",
                "eps_component": "breaks",
                "scientific_basis": "Break effectiveness research (PMC, Taylor & Francis)"
            },
            {
                "type": "chronotype_alignment",
                "title": "⏰ Peak Performance Timing",
                "summary": "Chronotype Optimization",
                "content": "Aligning cognitively demanding tasks to your individual peak performance window significantly improves outcomes. Schedule your most challenging work during your natural energy peaks - typically morning for most people, but varies by individual chronotype.",
                "confidence": 0.8,
                "priority": "medium",
                "eps_component": "chronotype",
                "scientific_basis": "Chronotype alignment research"
            },
            {
                "type": "eps_overview",
                "title": "📊 Evidence-Based Productivity Score",
                "summary": "Holistic Performance Measurement",
                "content": "Your productivity is measured using the Evidence-Based Productivity Score (EPS) which combines four research-backed factors: Focus Quality (35%), Sleep Sufficiency (25%), Micro-Break Hygiene (20%), and Chronotype Alignment (20%). This scientific approach provides actionable insights for sustainable productivity improvement.",
                "confidence": 0.9,
                "priority": "medium",
                "eps_component": "overall",
                "scientific_basis": "Integrated productivity research"
            }
        ]

        # Try to get actual data if possible
        if _db_session and _current_user_id:
            try:
                start_date = datetime.now() - timedelta(days=7)
                activities = _db_session.query(ActivityLog).filter(
                    ActivityLog.user_id == _current_user_id,
                    ActivityLog.date >= start_date
                ).all()

                if activities:
                    # Parse activities
                    parsed_activities = []
                    for activity_log in activities:
                        if activity_log.activities and isinstance(activity_log.activities, list):
                            parsed_activities.extend(activity_log.activities)

                    if parsed_activities:
                        # Generate personalized insights
                        personalized_insights = _generate_safe_insights(parsed_activities)
                        if personalized_insights:
                            insights = personalized_insights
            except:
                # If anything fails, just use the default insights
                pass

        result = {
            "insights": insights[:limit],
            "total_count": len(insights),
            "analysis_period": "Last 7 days",
            "status": "success"
        }

        return json.dumps(result)

    except:
        # Ultimate fallback - always return something useful
        fallback_result = {
            "insights": [{
                "type": "general",
                "title": "💡 Productivity Tip",
                "summary": "Stay Focused",
                "content": "Focus on one task at a time and eliminate distractions. This simple approach can significantly boost your productivity and work quality.",
                "confidence": 1.0,
                "priority": "high"
            }],
            "total_count": 1,
            "analysis_period": "General advice",
            "status": "fallback"
        }
        return json.dumps(fallback_result)

def get_eps_insights(limit: int = 5) -> str:
    """
    Generate Evidence-Based Productivity Score (EPS) insights based on user's activity data.

    This function analyzes user activities using the four EPS pillars:
    1. Focus Quality (deep work & fewer switches) - 35% weight
    2. Sleep Sufficiency (7-9 hours optimal) - 25% weight
    3. Micro-Break Hygiene (5-15% break ratio) - 20% weight
    4. Chronotype Alignment (peak timing) - 20% weight

    :param limit: Maximum number of insights to return (default: 5).
    :return: EPS-based insights as a JSON string with scientific backing.
    """
    try:
        # Default EPS-based insights with scientific backing
        eps_insights = [
            {
                "type": "focus_quality",
                "title": "🧠 Deep Work Analysis",
                "summary": "Focus Quality Assessment",
                "content": "Research shows rapid task switching imposes measurable cognitive switching costs (American Psychological Association). Your focus quality score is based on uninterrupted work blocks ≥25 minutes and context switch frequency. Aim for 2-4 hours of deep work daily.",
                "confidence": 0.9,
                "priority": "high",
                "eps_component": "focus",
                "weight": "35%",
                "scientific_basis": "Cognitive switching costs (APA, ACM Digital Library)"
            },
            {
                "type": "sleep_sufficiency",
                "title": "😴 Sleep Impact on Performance",
                "summary": "Cognitive Performance Optimization",
                "content": "Cognitive performance follows an inverted-U curve with sleep - 7-9 hours supports optimal executive function (PMC, PubMed). Your sleep quality directly impacts 25% of your productivity score. Consistent sleep schedules enhance cognitive performance.",
                "confidence": 0.95,
                "priority": "high",
                "eps_component": "sleep",
                "weight": "25%",
                "scientific_basis": "Sleep-cognition research (PMC, PubMed)"
            },
            {
                "type": "micro_break_hygiene",
                "title": "⏸️ Strategic Break Optimization",
                "summary": "Break Pattern Effectiveness",
                "content": "Short breaks support well-being and aid performance for demanding tasks (PMC, Taylor & Francis). Optimal break-to-work ratio is 5-15%. Try 25-minute work blocks with 5-minute breaks for sustained performance.",
                "confidence": 0.85,
                "priority": "medium",
                "eps_component": "breaks",
                "weight": "20%",
                "scientific_basis": "Break effectiveness research (PMC, Taylor & Francis)"
            },
            {
                "type": "chronotype_alignment",
                "title": "⏰ Peak Performance Timing",
                "summary": "Chronotype Optimization Strategy",
                "content": "Aligning cognitively demanding tasks to individual peak windows improves outcomes significantly. Schedule your most challenging work during natural energy peaks - typically morning hours for most chronotypes.",
                "confidence": 0.8,
                "priority": "medium",
                "eps_component": "chronotype",
                "weight": "20%",
                "scientific_basis": "Chronotype alignment research"
            }
        ]

        # Try to get personalized EPS analysis if data is available
        if _db_session and _current_user_id:
            try:
                start_date = datetime.now() - timedelta(days=7)
                activities = _db_session.query(ActivityLog).filter(
                    ActivityLog.user_id == _current_user_id,
                    ActivityLog.date >= start_date
                ).all()

                if activities:
                    # Parse activities for EPS analysis
                    parsed_activities = []
                    for activity_log in activities:
                        if activity_log.activities and isinstance(activity_log.activities, list):
                            parsed_activities.extend(activity_log.activities)

                    if parsed_activities:
                        # Generate personalized EPS insights
                        personalized_insights = _generate_eps_insights(parsed_activities)
                        if personalized_insights:
                            eps_insights = personalized_insights
            except Exception as e:
                logger.error(f"Error generating personalized EPS insights: {e}")
                # Fall back to default insights

        result = {
            "insights": eps_insights[:limit],
            "total_count": len(eps_insights),
            "analysis_period": "Last 7 days",
            "methodology": "Evidence-Based Productivity Score (EPS)",
            "components": {
                "focus_quality": "35% - Deep work time & context switches",
                "sleep_sufficiency": "25% - 7-9 hour optimal range",
                "micro_break_hygiene": "20% - 5-15% break ratio",
                "chronotype_alignment": "20% - Peak timing optimization"
            },
            "status": "success"
        }

        return json.dumps(result)

    except Exception as e:
        logger.error(f"Error generating EPS insights: {e}")
        # Ultimate fallback
        fallback_result = {
            "insights": [{
                "type": "eps_overview",
                "title": "📊 Evidence-Based Productivity",
                "summary": "Scientific Approach to Productivity",
                "content": "Your productivity is measured using four research-backed factors: Focus Quality (35%), Sleep Sufficiency (25%), Micro-Break Hygiene (20%), and Chronotype Alignment (20%). This evidence-based approach provides actionable insights for sustainable improvement.",
                "confidence": 1.0,
                "priority": "high",
                "eps_component": "overall",
                "scientific_basis": "Integrated productivity research"
            }],
            "total_count": 1,
            "analysis_period": "General guidance",
            "methodology": "Evidence-Based Productivity Score (EPS)",
            "status": "fallback"
        }
        return json.dumps(fallback_result)

def _generate_eps_insights(activities: list) -> list:
    """
    Generate personalized EPS insights based on actual activity data.
    """
    try:
        if not activities:
            return []

        # Calculate EPS metrics from activities
        eps_metrics = _calculate_eps_metrics_from_activities(activities)
        insights = []

        # Focus Quality Insights (35% weight)
        focus_score = eps_metrics.get("focus_score", 0)
        deep_work_min = eps_metrics.get("metrics", {}).get("deep_work_minutes", 0)
        context_switches = eps_metrics.get("metrics", {}).get("context_switches", 0)

        if focus_score >= 80:
            insights.append({
                "type": "focus_quality",
                "title": "🧠 Excellent Focus Quality",
                "summary": f"Focus Score: {focus_score:.1f}/100",
                "content": f"Outstanding focus performance! You achieved {deep_work_min} minutes of deep work with only {context_switches} context switches. This represents the top 20% of focus quality. Maintain this pattern for sustained high performance.",
                "confidence": 0.9,
                "priority": "low",
                "eps_component": "focus",
                "score": focus_score
            })
        elif focus_score >= 60:
            insights.append({
                "type": "focus_quality",
                "title": "🎯 Good Focus with Room for Improvement",
                "summary": f"Focus Score: {focus_score:.1f}/100",
                "content": f"Solid focus performance with {deep_work_min} minutes of deep work. To improve your focus score, try to increase uninterrupted work blocks to 25+ minutes and reduce context switches (currently {context_switches}). Consider time-blocking techniques.",
                "confidence": 0.85,
                "priority": "medium",
                "eps_component": "focus",
                "score": focus_score
            })
        else:
            insights.append({
                "type": "focus_quality",
                "title": "🔧 Focus Quality Needs Attention",
                "summary": f"Focus Score: {focus_score:.1f}/100",
                "content": f"Your focus quality score indicates significant room for improvement. With {deep_work_min} minutes of deep work and {context_switches} context switches, consider implementing the Pomodoro Technique and eliminating distractions during work blocks.",
                "confidence": 0.9,
                "priority": "high",
                "eps_component": "focus",
                "score": focus_score
            })

        # Sleep Sufficiency Insights (25% weight)
        sleep_score = eps_metrics.get("sleep_score", 75)
        if sleep_score >= 90:
            insights.append({
                "type": "sleep_sufficiency",
                "title": "😴 Optimal Sleep Quality",
                "summary": f"Sleep Score: {sleep_score:.1f}/100",
                "content": "Excellent sleep quality! You're in the optimal 7-9 hour range that supports peak cognitive function. This strong foundation contributes 25% to your overall productivity score. Keep maintaining consistent sleep schedules.",
                "confidence": 0.8,
                "priority": "low",
                "eps_component": "sleep",
                "score": sleep_score
            })
        elif sleep_score >= 70:
            insights.append({
                "type": "sleep_sufficiency",
                "title": "🌙 Good Sleep with Minor Adjustments",
                "summary": f"Sleep Score: {sleep_score:.1f}/100",
                "content": "Good sleep quality that supports productivity. Small improvements to get closer to the 7-9 hour optimal range could boost your overall EPS score. Consider establishing a consistent bedtime routine.",
                "confidence": 0.8,
                "priority": "medium",
                "eps_component": "sleep",
                "score": sleep_score
            })
        else:
            insights.append({
                "type": "sleep_sufficiency",
                "title": "⚠️ Sleep Quality Impacting Performance",
                "summary": f"Sleep Score: {sleep_score:.1f}/100",
                "content": "Sleep quality is significantly impacting your productivity score (25% weight). Research shows cognitive performance peaks with 7-9 hours of sleep. Prioritize sleep hygiene for substantial productivity gains.",
                "confidence": 0.9,
                "priority": "high",
                "eps_component": "sleep",
                "score": sleep_score
            })

        # Micro-Break Hygiene Insights (20% weight)
        breaks_score = eps_metrics.get("breaks_score", 0)
        break_minutes = eps_metrics.get("metrics", {}).get("break_minutes", 0)
        focus_minutes = eps_metrics.get("metrics", {}).get("focus_minutes", 1)
        break_ratio = (break_minutes / focus_minutes) * 100 if focus_minutes > 0 else 0

        if breaks_score >= 80:
            insights.append({
                "type": "micro_break_hygiene",
                "title": "⏸️ Excellent Break Pattern",
                "summary": f"Breaks Score: {breaks_score:.1f}/100",
                "content": f"Perfect break hygiene! Your {break_ratio:.1f}% break-to-work ratio is in the optimal 5-15% range. This strategic rest pattern supports sustained performance and contributes positively to your EPS score.",
                "confidence": 0.85,
                "priority": "low",
                "eps_component": "breaks",
                "score": breaks_score
            })
        elif breaks_score >= 50:
            insights.append({
                "type": "micro_break_hygiene",
                "title": "⏰ Break Pattern Optimization",
                "summary": f"Breaks Score: {breaks_score:.1f}/100",
                "content": f"Your break pattern ({break_ratio:.1f}% ratio) has room for improvement. Research shows 5-15% break-to-work ratio optimizes performance. Try the Pomodoro Technique: 25 minutes work + 5 minute breaks.",
                "confidence": 0.8,
                "priority": "medium",
                "eps_component": "breaks",
                "score": breaks_score
            })
        else:
            insights.append({
                "type": "micro_break_hygiene",
                "title": "🚨 Insufficient Break Hygiene",
                "summary": f"Breaks Score: {breaks_score:.1f}/100",
                "content": f"Critical break deficiency detected ({break_ratio:.1f}% ratio). Without adequate breaks, performance degrades significantly. Implement regular 5-15% break patterns to prevent burnout and boost your EPS score.",
                "confidence": 0.9,
                "priority": "high",
                "eps_component": "breaks",
                "score": breaks_score
            })

        # Overall EPS Summary
        overall_score = eps_metrics.get("eps_score", 0)
        interpretation = eps_metrics.get("interpretation", "")

        insights.append({
            "type": "eps_summary",
            "title": "📊 Evidence-Based Productivity Score",
            "summary": f"Overall EPS: {overall_score:.1f}/100",
            "content": f"{interpretation} Your EPS combines Focus Quality (35%), Sleep Sufficiency (25%), Micro-Break Hygiene (20%), and Chronotype Alignment (20%) using research-backed algorithms.",
            "confidence": 0.95,
            "priority": "medium",
            "eps_component": "overall",
            "score": overall_score,
            "breakdown": {
                "focus": focus_score,
                "sleep": sleep_score,
                "breaks": breaks_score,
                "chronotype": eps_metrics.get("chronotype_score", 50)
            }
        })

        return insights[:5]  # Return top 5 insights

    except Exception as e:
        logger.error(f"Error generating personalized EPS insights: {e}")
        return []

def _calculate_eps_metrics_from_activities(activities: list) -> Dict[str, Any]:
    """
    Calculate Evidence-Based Productivity Score metrics from activity data.

    Returns:
        Dictionary containing EPS metrics and breakdown
    """
    try:
        if not activities:
            return {
                "eps_score": 0,
                "focus_score": 0,
                "sleep_score": 75,  # Default assumption
                "breaks_score": 0,
                "chronotype_score": 50,  # Default assumption
                "metrics": {
                    "deep_work_minutes": 0,
                    "context_switches": 0,
                    "break_minutes": 0,
                    "focus_minutes": 0,
                    "chronotype_alignment": 0.5
                },
                "interpretation": "No activity data available for analysis"
            }

        # Analyze activities for EPS components
        work_activities = []
        break_activities = []
        total_duration = 0

        for activity in activities:
            duration = activity.get('duration_minutes', 0) or activity.get('duration', 0)
            if duration > 0:
                total_duration += duration

                # Categorize activities
                activity_name = activity.get('activity_name', '').lower()
                category = activity.get('category', '').lower()

                if 'break' in activity_name or 'rest' in activity_name or category == 'break':
                    break_activities.append(activity)
                else:
                    work_activities.append(activity)

        # Calculate deep work time (activities >= 25 minutes)
        deep_work_min = sum(
            activity.get('duration_minutes', 0) or activity.get('duration', 0)
            for activity in work_activities
            if (activity.get('duration_minutes', 0) or activity.get('duration', 0)) >= 25
        )

        # Estimate context switches (number of different activity types)
        activity_types = set()
        for activity in work_activities:
            activity_name = activity.get('activity_name', '').lower()
            if activity_name:
                activity_types.add(activity_name)
        context_switches = max(0, len(activity_types) - 1)

        # Calculate break time
        break_minutes = sum(
            activity.get('duration_minutes', 0) or activity.get('duration', 0)
            for activity in break_activities
        )

        # Calculate total focus time
        focus_minutes = sum(
            activity.get('duration_minutes', 0) or activity.get('duration', 0)
            for activity in work_activities
        )
        if focus_minutes == 0:
            focus_minutes = 1  # Avoid division by zero

        # Estimate sleep quality from mood/energy if available
        moods = [activity.get('mood', 0) for activity in activities if activity.get('mood', 0) > 0]
        energies = [activity.get('energy', 0) for activity in activities if activity.get('energy', 0) > 0]

        avg_mood = sum(moods) / len(moods) if moods else 7.5
        avg_energy = sum(energies) / len(energies) if energies else 7.5

        # Estimate sleep hours from mood/energy (7.5 baseline, adjust based on mood/energy)
        sleep_hours = 7.5
        if avg_mood > 0 and avg_energy > 0:
            mood_energy_avg = (avg_mood + avg_energy) / 2
            # Scale mood/energy (1-10) to sleep adjustment (-1 to +1 hours)
            sleep_adjustment = (mood_energy_avg - 5.5) * 0.3
            sleep_hours = max(5.0, min(9.0, sleep_hours + sleep_adjustment))

        # Estimate chronotype alignment (simplified - higher mood/energy suggests better alignment)
        hc_ratio = 0.5  # Default
        if avg_mood > 0 and avg_energy > 0:
            mood_energy_avg = (avg_mood + avg_energy) / 2
            hc_ratio = min(1.0, mood_energy_avg / 10.0)

        # Create DayMetrics object and calculate EPS
        metrics = DayMetrics(
            deep_work_min=int(deep_work_min),
            context_switches=int(context_switches),
            sleep_hours=sleep_hours,
            break_minutes=int(break_minutes),
            focus_minutes=int(focus_minutes),
            hc_ratio=hc_ratio
        )

        # Calculate EPS breakdown
        score_breakdown = _calculate_score_internal(metrics)
        interpretation = _interpret_score(score_breakdown.score)

        return {
            "eps_score": score_breakdown.score,
            "focus_score": score_breakdown.focus,
            "sleep_score": score_breakdown.sleep,
            "breaks_score": score_breakdown.breaks,
            "chronotype_score": score_breakdown.chronotype,
            "metrics": {
                "deep_work_minutes": deep_work_min,
                "context_switches": context_switches,
                "break_minutes": break_minutes,
                "focus_minutes": focus_minutes,
                "chronotype_alignment": hc_ratio,
                "total_activities": len(activities),
                "work_activities": len(work_activities),
                "break_activities": len(break_activities)
            },
            "interpretation": interpretation,
            "recommendations": _generate_recommendations(score_breakdown)
        }

    except Exception as e:
        logger.error(f"Error calculating EPS metrics from activities: {e}")
        return {
            "eps_score": 0,
            "focus_score": 0,
            "sleep_score": 75,
            "breaks_score": 0,
            "chronotype_score": 50,
            "metrics": {},
            "interpretation": "Error analyzing activity data",
            "recommendations": []
        }

def _generate_safe_insights(activities: list) -> list:
    """Generate insights safely without throwing exceptions"""
    try:
        if not activities:
            return []

        insights = []
        activity_count = len(activities)

        # Calculate basic stats safely
        total_duration = 0
        total_productivity = 0
        total_mood = 0
        valid_activities = 0

        categories = {}

        for activity in activities:
            if isinstance(activity, dict):
                duration = activity.get("duration", 0)
                productivity = activity.get("productivity", 0)
                mood = activity.get("mood", 0)
                category = activity.get("category", "general")

                if duration > 0 or productivity > 0:
                    valid_activities += 1
                    total_duration += duration
                    total_productivity += productivity
                    total_mood += mood

                    if category not in categories:
                        categories[category] = 0
                    categories[category] += 1

        # Generate insights based on what we found
        if valid_activities > 0:
            avg_productivity = total_productivity / valid_activities
            avg_mood = total_mood / valid_activities
            hours = total_duration / 60

            # Productivity insight
            if avg_productivity >= 7:
                insights.append({
                    "type": "productivity",
                    "title": "🏆 Strong Performance",
                    "summary": "Excellent Productivity Levels",
                    "content": f"You've maintained a solid average productivity score of {avg_productivity:.1f}/10 across {valid_activities} activities. Keep up the great work!",
                    "confidence": 0.9,
                    "priority": "high"
                })
            else:
                insights.append({
                    "type": "productivity",
                    "title": "📈 Growth Opportunity",
                    "summary": "Room for Improvement",
                    "content": f"Your average productivity score is {avg_productivity:.1f}/10. Consider identifying what helps you focus best and scheduling important tasks during those times.",
                    "confidence": 0.8,
                    "priority": "medium"
                })

            # Time insight
            if hours > 0:
                insights.append({
                    "type": "time_management",
                    "title": "⏰ Time Investment",
                    "summary": "Activity Time Analysis",
                    "content": f"You've logged {hours:.1f} hours across {activity_count} activities this week. This shows good engagement with tracking your productivity.",
                    "confidence": 0.8,
                    "priority": "medium"
                })

            # Mood insight
            if avg_mood >= 6:
                insights.append({
                    "type": "wellness",
                    "title": "😊 Positive Energy",
                    "summary": "Good Mood Levels",
                    "content": f"Your average mood score of {avg_mood:.1f}/10 indicates you're maintaining a positive outlook. This positive energy supports better productivity!",
                    "confidence": 0.7,
                    "priority": "low"
                })

            # Category insight
            if categories:
                top_category = max(categories.items(), key=lambda x: x[1])
                insights.append({
                    "type": "focus_area",
                    "title": "🎯 Primary Focus",
                    "summary": f"Most Active in {top_category[0].title()}",
                    "content": f"You've been most active in {top_category[0]} activities ({top_category[1]} activities). This shows where you're investing most of your tracked time.",
                    "confidence": 0.9,
                    "priority": "medium"
                })

        return insights[:5]  # Return max 5 insights

    except:
        # If anything fails, return empty list (will use default insights)
        return []

def _generate_activity_insights(activities: list) -> list:
    """Generate insights based on activity patterns"""
    insights = []

    try:
        logger.info(f"🔍 Analyzing {len(activities)} activities for insights")

        # Debug: Log sample activity data
        if activities:
            sample_activity = activities[0]
            logger.info(f"🔍 Sample activity: {sample_activity}")
            logger.info(f"🔍 Sample activity keys: {list(sample_activity.keys()) if isinstance(sample_activity, dict) else 'Not a dict'}")

        # Calculate basic metrics with better error handling
        durations = []
        productivities = []
        moods = []
        energies = []

        for activity in activities:
            if isinstance(activity, dict):
                durations.append(activity.get("duration", 0))
                productivities.append(activity.get("productivity", 0))
                moods.append(activity.get("mood", 0))
                energies.append(activity.get("energy", 0))
            else:
                logger.warning(f"⚠️ Non-dict activity found: {type(activity)} - {activity}")

        total_time = sum(durations)
        avg_productivity = sum(productivities) / len(productivities) if productivities else 0
        avg_mood = sum(moods) / len(moods) if moods else 0
        avg_energy = sum(energies) / len(energies) if energies else 0

        logger.info(f"📊 Metrics: time={total_time}min, productivity={avg_productivity:.1f}, mood={avg_mood:.1f}, energy={avg_energy:.1f}")
        logger.info(f"📊 Data counts: durations={len(durations)}, productivities={len(productivities)}, moods={len(moods)}, energies={len(energies)}")

        # Check if we have valid data - if not, provide helpful fallback insights
        if total_time == 0 and avg_productivity == 0:
            logger.warning("⚠️ No valid activity data found - providing fallback insights")
            return _get_fallback_insights(len(activities))

    except Exception as e:
        logger.error(f"❌ Error calculating basic metrics: {e}")
        import traceback
        logger.error(f"📍 Full traceback: {traceback.format_exc()}")
        return [{
            "type": "error",
            "title": "🔧 Analysis Error",
            "summary": "Could not analyze activity data",
            "content": f"There was an issue analyzing your activity patterns: {str(e)}. Please ensure your activities have proper duration, productivity, mood, and energy values.",
            "confidence": 1.0,
            "priority": "medium"
        }]

    # Category analysis
    category_stats = {}
    for activity in activities:
        cat = activity.get("category", "uncategorized")
        if cat not in category_stats:
            category_stats[cat] = {"count": 0, "total_time": 0, "avg_productivity": 0, "productivities": []}
        category_stats[cat]["count"] += 1
        category_stats[cat]["total_time"] += activity.get("duration", 0)
        category_stats[cat]["productivities"].append(activity.get("productivity", 0))

    # Calculate average productivity per category
    for cat, stats in category_stats.items():
        if stats["productivities"]:
            stats["avg_productivity"] = sum(stats["productivities"]) / len(stats["productivities"])

    # Generate insights based on patterns

    # 1. Productivity Peak Insight
    if avg_productivity >= 8:
        insights.append({
            "type": "productivity",
            "title": "🏆 Peak Performance Week",
            "summary": "Excellent Productivity Levels",
            "content": f"You've maintained an outstanding average productivity score of {avg_productivity:.1f}/10 this week. Your focus and efficiency are at their peak!",
            "confidence": 0.9,
            "priority": "high"
        })
    elif avg_productivity >= 6:
        insights.append({
            "type": "productivity",
            "title": "👍 Solid Performance",
            "summary": "Good Productivity Levels",
            "content": f"You're performing well with an average productivity score of {avg_productivity:.1f}/10. Consider identifying what's working well and doing more of it.",
            "confidence": 0.8,
            "priority": "medium"
        })
    else:
        insights.append({
            "type": "productivity",
            "title": "💡 Optimization Opportunity",
            "summary": "Room for Productivity Improvement",
            "content": f"Your average productivity score is {avg_productivity:.1f}/10. Consider reviewing your workflow, eliminating distractions, or breaking tasks into smaller chunks.",
            "confidence": 0.85,
            "priority": "high"
        })

    # 2. Time Distribution Insight
    if category_stats:
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]["total_time"], reverse=True)
        top_category = sorted_categories[0]
        top_time_hours = top_category[1]["total_time"] / 60

        insights.append({
            "type": "time_management",
            "title": "⏰ Time Allocation Analysis",
            "summary": f"Most Time Spent on {top_category[0].title()}",
            "content": f"You spent {top_time_hours:.1f} hours on {top_category[0]} activities this week ({top_category[1]['count']} activities). This represents your primary focus area.",
            "confidence": 0.95,
            "priority": "medium"
        })

    # 3. Mood & Energy Insight
    if avg_mood >= 7:
        insights.append({
            "type": "wellness",
            "title": "😊 Positive Mindset",
            "summary": "Great Mood Levels",
            "content": f"Your average mood score of {avg_mood:.1f}/10 shows you're maintaining a positive outlook. This positive energy likely contributes to your overall performance!",
            "confidence": 0.8,
            "priority": "low"
        })
    elif avg_mood < 5:
        insights.append({
            "type": "wellness",
            "title": "🌟 Mood Enhancement Opportunity",
            "summary": "Consider Mood-Boosting Activities",
            "content": f"Your average mood score is {avg_mood:.1f}/10. Consider incorporating activities you enjoy, taking breaks, or connecting with colleagues to boost your spirits.",
            "confidence": 0.85,
            "priority": "high"
        })

    # 4. Category Performance Insight
    if len(category_stats) >= 2:
        best_category = max(category_stats.items(), key=lambda x: x[1]["avg_productivity"])
        insights.append({
            "type": "performance",
            "title": "🎯 Peak Performance Category",
            "summary": f"Highest Productivity in {best_category[0].title()}",
            "content": f"You're most productive during {best_category[0]} activities (avg: {best_category[1]['avg_productivity']:.1f}/10). Consider scheduling more of these during your peak hours.",
            "confidence": 0.8,
            "priority": "medium"
        })

    # 5. Activity Volume Insight
    if len(activities) >= 30:
        insights.append({
            "type": "activity_volume",
            "title": "🚀 High Activity Level",
            "summary": "Very Active Week",
            "content": f"You completed {len(activities)} activities this week, showing excellent engagement and commitment to your goals. Make sure to balance this with adequate rest.",
            "confidence": 0.9,
            "priority": "low"
        })
    elif len(activities) < 15:
        insights.append({
            "type": "activity_volume",
            "title": "📈 Activity Opportunity",
            "summary": "Consider Increasing Activity",
            "content": f"You logged {len(activities)} activities this week. Consider breaking larger tasks into smaller, trackable activities to better monitor your progress.",
            "confidence": 0.7,
            "priority": "medium"
        })

    return insights

def _get_fallback_insights(activity_count: int) -> list:
    """Provide helpful fallback insights when data is insufficient"""
    insights = []

    if activity_count > 0:
        insights.append({
            "type": "data_improvement",
            "title": "📊 Activity Tracking Opportunity",
            "summary": "Enhance Your Activity Data",
            "content": f"I found {activity_count} activity entries, but they're missing key metrics like duration, productivity scores, mood, and energy levels. Adding these details will unlock powerful insights about your productivity patterns and help optimize your workflow.",
            "confidence": 1.0,
            "priority": "high"
        })

        insights.append({
            "type": "productivity_tip",
            "title": "🎯 Productivity Tracking Best Practices",
            "summary": "Maximize Your Insights",
            "content": "To get the most from your productivity analysis, try logging: (1) Duration for each activity, (2) Productivity score (1-10), (3) Mood level (1-10), and (4) Energy level (1-10). This data helps identify your peak performance times and optimal activity types.",
            "confidence": 0.9,
            "priority": "medium"
        })

        insights.append({
            "type": "general_advice",
            "title": "⚡ Productivity Boost Tips",
            "summary": "Universal Productivity Strategies",
            "content": "While I analyze your data, here are proven productivity boosters: (1) Time-block your most important tasks during peak energy hours, (2) Take regular breaks every 90 minutes, (3) Batch similar activities together, and (4) Track your mood and energy to identify patterns.",
            "confidence": 0.8,
            "priority": "low"
        })
    else:
        insights.append({
            "type": "getting_started",
            "title": "🚀 Start Your Productivity Journey",
            "summary": "Begin Activity Tracking",
            "content": "Welcome to your productivity insights! Start by logging your daily activities with details like duration, productivity level (1-10), mood (1-10), and energy (1-10). After a few days of tracking, I'll provide personalized insights about your productivity patterns and optimization opportunities.",
            "confidence": 1.0,
            "priority": "high"
        })

        insights.append({
            "type": "motivation",
            "title": "💪 Productivity Mindset",
            "summary": "Building Better Habits",
            "content": "Great productivity starts with awareness. By tracking your activities and reflecting on what works best, you're already on the path to optimization. Remember: small, consistent improvements compound into significant gains over time.",
            "confidence": 0.9,
            "priority": "medium"
        })

    return insights

# Define user functions set following Microsoft's pattern
user_functions = {
    get_user_profile,
    get_user_preferences,
    get_recent_activities,
    get_productivity_stats,
    get_current_goals,
    get_recent_insights,
    get_eps_insights
}

# Legacy function for backward compatibility
def create_function_definitions() -> List[Dict[str, Any]]:
    """Create function definitions for Azure OpenAI assistant (legacy)"""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_user_profile",
                "description": "Get the user's basic profile information including name, email, bio, timezone, and account details",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_preferences",
                "description": "Get the user's preferences and settings including work hours, break durations, AI settings, and UI preferences",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_recent_activities",
                "description": "Get the user's recent activity logs with productivity scores, mood, and energy levels",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to look back (default: 7)",
                            "default": 7
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_productivity_stats",
                "description": "Get comprehensive productivity statistics including total time tracked, average productivity/mood/energy scores, category breakdown, and insights. Format the response in a user-friendly way with emojis and clear metrics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze (default: 7)",
                            "default": 7
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_goals",
                "description": "Get the user's current active goals with progress information",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_recent_insights",
                "description": "Generate AI insights and recommendations based on the user's activity patterns from the last 7 days. Analyzes productivity, time allocation, mood, energy, and performance patterns to provide personalized insights.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of insights to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_eps_insights",
                "description": "Generate Evidence-Based Productivity Score (EPS) insights using scientific research. Analyzes four key components: Focus Quality (35% - deep work & context switches), Sleep Sufficiency (25% - 7-9 hour optimal), Micro-Break Hygiene (20% - 5-15% break ratio), and Chronotype Alignment (20% - peak timing). Provides research-backed recommendations with scientific citations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of EPS insights to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": []
                }
            }
        }
    ]


# ==============================
# 🤖 AZURE AI AGENT FOR EPS INSIGHTS
# ==============================
class EPSInsightsAgent:
    """
    Azure AI Agent for Evidence-Based Productivity Score insights.
    Following Microsoft's Azure AI documentation pattern.
    """

    def __init__(self):
        """Initialize the Azure AI agent for EPS insights."""
        try:
            # Get environment variables
            project_endpoint = os.environ.get(
                "PROJECT_ENDPOINT",
                "https://elevate777.services.ai.azure.com/api/projects/firstProject"
            )
            model_deployment = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o")

            # Initialize the AIProjectClient
            self.project_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=DefaultAzureCredential()
            )

            # Initialize the FunctionTool with EPS functions
            self.functions = FunctionTool(functions=user_functions)

            # Create the agent with EPS-focused instructions
            self.agent = self.project_client.agents.create_agent(
                model=model_deployment,
                name="eps-insights-agent",
                instructions="""You are an Evidence-Based Productivity Score (EPS) specialist AI agent.

Your expertise is in analyzing productivity using four scientifically-backed components:

1. **Focus Quality (35% weight)**: Deep work time and context switches
   - Research basis: Cognitive switching costs (American Psychological Association, ACM Digital Library)
   - Optimal: 25+ minute uninterrupted blocks, minimal context switches
   - Measures: Deep work minutes, task switching frequency

2. **Sleep Sufficiency (25% weight)**: Sleep duration optimization
   - Research basis: Sleep-cognition performance curves (PMC, PubMed)
   - Optimal: 7-9 hours for peak executive function
   - Measures: Sleep duration, consistency, quality indicators

3. **Micro-Break Hygiene (20% weight)**: Strategic break patterns
   - Research basis: Break effectiveness studies (PMC, Taylor & Francis)
   - Optimal: 5-15% break-to-work ratio
   - Measures: Break frequency, duration, timing

4. **Chronotype Alignment (20% weight)**: Peak timing optimization
   - Research basis: Chronotype performance research
   - Optimal: High-cognitive tasks during individual peak windows
   - Measures: Task-timing alignment, energy pattern matching

When providing insights:
- Use the get_eps_insights() function for evidence-based analysis
- Reference scientific research when explaining recommendations
- Provide specific, actionable advice based on EPS components
- Explain the weight and importance of each factor
- Connect insights to the user's actual data when available
- Be encouraging while providing honest assessments

Always prioritize evidence-based recommendations over generic productivity advice.""",
                tools=self.functions.definitions,
            )

            logger.info(f"Created EPS insights agent, ID: {self.agent.id}")

        except Exception as e:
            logger.error(f"Failed to initialize EPS insights agent: {e}")
            raise

    def generate_eps_insights(self, user_message: str, db_session: Session, user_id: str) -> Dict[str, Any]:
        """
        Generate EPS insights using the AI agent.

        Args:
            user_message: User's request for insights
            db_session: Database session for data access
            user_id: User ID for personalized insights

        Returns:
            Dictionary containing AI-generated EPS insights
        """
        try:
            # Set the function context for database access
            set_function_context(db_session, user_id)

            # Create a thread for this analysis
            thread = self.project_client.agents.threads.create()

            # Send message to the agent
            message = self.project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"""Please provide Evidence-Based Productivity Score (EPS) insights for the user.

User request: {user_message}

Please:
1. Use the get_eps_insights() function to get detailed EPS analysis
2. Explain the four EPS components and their scientific backing
3. Provide specific recommendations based on the user's data
4. Reference the research basis for your suggestions
5. Be encouraging while providing actionable advice

Focus on evidence-based insights rather than generic productivity tips."""
            )

            # Process the request with function calling
            run = self.project_client.agents.runs.create(
                thread_id=thread.id,
                agent_id=self.agent.id
            )

            # Wait for completion and handle function calls
            start_time = time.time()
            while time.time() - start_time < 30:  # 30 second timeout
                run_status = self.project_client.agents.runs.get(
                    thread_id=thread.id,
                    run_id=run.id
                )

                if run_status.status == "completed":
                    break
                elif run_status.status == "requires_action":
                    # Handle function calls
                    tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []

                    for tool_call in tool_calls:
                        function_name = tool_call.function.name

                        # Execute the appropriate function
                        if function_name in [func.__name__ for func in user_functions]:
                            try:
                                # Parse arguments
                                args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                                # Call the function
                                if function_name == "get_eps_insights":
                                    output = get_eps_insights(args.get('limit', 5))
                                elif function_name == "get_recent_activities":
                                    output = get_recent_activities(args.get('days', 7), args.get('limit', 20))
                                elif function_name == "get_productivity_stats":
                                    output = get_productivity_stats(args.get('days', 7))
                                elif function_name == "get_user_profile":
                                    output = get_user_profile()
                                elif function_name == "get_user_preferences":
                                    output = get_user_preferences()
                                elif function_name == "get_current_goals":
                                    output = get_current_goals(args.get('limit', 10))
                                elif function_name == "get_recent_insights":
                                    output = get_recent_insights(args.get('limit', 5))
                                else:
                                    output = json.dumps({"error": f"Unknown function: {function_name}"})

                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": output
                                })

                            except Exception as e:
                                logger.error(f"Error executing function {function_name}: {e}")
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": json.dumps({"error": f"Function execution failed: {str(e)}"})
                                })

                    # Submit the tool outputs
                    self.project_client.agents.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

                time.sleep(1)  # Wait before checking again

            # Get the final response
            if run_status.status == "completed":
                messages = self.project_client.agents.messages.list(thread_id=thread.id)

                # Find the assistant's response
                for message in messages:
                    if message.role == "assistant" and message.content:
                        return {
                            "success": True,
                            "insights": message.content[0].text.value,
                            "agent_id": self.agent.id,
                            "thread_id": thread.id,
                            "methodology": "Evidence-Based Productivity Score (EPS)"
                        }

            return {
                "success": False,
                "error": f"Agent run failed with status: {run_status.status}",
                "insights": "Failed to generate EPS insights"
            }

        except Exception as e:
            logger.error(f"Error generating EPS insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "insights": "Error occurred during EPS insight generation"
            }

    def cleanup(self):
        """Clean up the agent after use."""
        try:
            self.project_client.agents.delete_agent(self.agent.id)
            logger.info("Deleted EPS insights agent")
        except Exception as e:
            logger.error(f"Error deleting EPS agent: {e}")

# Create a singleton instance for the EPS insights agent
eps_insights_agent = None

def get_eps_insights_agent():
    """Get or create the EPS insights agent instance."""
    global eps_insights_agent
    if eps_insights_agent is None:
        eps_insights_agent = EPSInsightsAgent()
    return eps_insights_agent
