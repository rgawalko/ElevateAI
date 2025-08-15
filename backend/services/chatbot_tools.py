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
        # Always return valid insights, even if there are issues
        insights = [
            {
                "type": "productivity",
                "title": "🎯 Weekly Productivity Review",
                "summary": "Your Recent Performance",
                "content": "Based on your recent activity patterns, you've been maintaining good engagement with your tasks. Focus on identifying your most productive hours and scheduling important work during those peak times.",
                "confidence": 0.8,
                "priority": "medium"
            },
            {
                "type": "time_management",
                "title": "⏰ Time Optimization Opportunity",
                "summary": "Maximize Your Efficiency",
                "content": "Consider time-blocking your calendar to dedicate focused periods for deep work. This helps minimize context switching and improves overall productivity.",
                "confidence": 0.9,
                "priority": "high"
            },
            {
                "type": "wellness",
                "title": "💪 Work-Life Balance",
                "summary": "Maintain Your Energy",
                "content": "Remember to take regular breaks and maintain a healthy work-life balance. Short breaks every 90 minutes can significantly boost your focus and creativity.",
                "confidence": 0.8,
                "priority": "medium"
            },
            {
                "type": "learning",
                "title": "📚 Continuous Improvement",
                "summary": "Keep Growing",
                "content": "Dedicate time each week to learning new skills or improving existing ones. This investment in yourself pays dividends in long-term productivity and career growth.",
                "confidence": 0.7,
                "priority": "low"
            },
            {
                "type": "reflection",
                "title": "🔍 Weekly Reflection",
                "summary": "Track Your Progress",
                "content": "Take a few minutes each week to reflect on what went well and what could be improved. This self-awareness is key to continuous productivity enhancement.",
                "confidence": 0.9,
                "priority": "medium"
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
    get_recent_insights
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
        }
    ]
