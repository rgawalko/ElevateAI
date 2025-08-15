#!/usr/bin/env python3
"""
Script to create sample data for testing chatbot function calling
"""

import sys
import os
import uuid
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.user import User
from models.activity_log import ActivityLog
from models.goal import Goal
from models.ai_insight import AIInsight
import random

def create_sample_data():
    """Create sample data for testing chatbot function calling"""
    
    db = SessionLocal()
    
    try:
        print("🚀 Creating sample data for chatbot testing...")
        
        # Get Alice (first demo user) for sample data
        alice = db.query(User).filter(User.email == "alice@elevate-ai.com").first()
        if not alice:
            print("❌ Alice demo user not found. Please run create_demo_users.py first.")
            return
        
        print(f"👤 Creating sample data for user: {alice.name}")
        
        # Create sample activity logs (last 7 days)
        activities_data = [
            {"name": "Morning Planning", "category": "planning", "duration": 30, "productivity": 8, "mood": 7, "energy": 8},
            {"name": "Code Review", "category": "work", "duration": 90, "productivity": 9, "mood": 8, "energy": 7},
            {"name": "Team Meeting", "category": "meeting", "duration": 60, "productivity": 6, "mood": 6, "energy": 6},
            {"name": "Feature Development", "category": "work", "duration": 180, "productivity": 9, "mood": 8, "energy": 8},
            {"name": "Lunch Break", "category": "break", "duration": 45, "productivity": 5, "mood": 9, "energy": 9},
            {"name": "Email Processing", "category": "communication", "duration": 30, "productivity": 7, "mood": 6, "energy": 6},
            {"name": "Documentation", "category": "work", "duration": 120, "productivity": 8, "mood": 7, "energy": 7},
            {"name": "Learning Session", "category": "learning", "duration": 60, "productivity": 9, "mood": 9, "energy": 8},
            {"name": "Exercise", "category": "health", "duration": 45, "productivity": 10, "mood": 10, "energy": 10},
            {"name": "Project Planning", "category": "planning", "duration": 75, "productivity": 8, "mood": 7, "energy": 7},
        ]
        
        created_activities = 0
        for i in range(7):  # Last 7 days
            day_offset = i
            base_date = datetime.now(timezone.utc) - timedelta(days=day_offset)
            
            # Create 3-5 activities per day
            daily_activities = random.sample(activities_data, random.randint(3, 5))
            
            for j, activity_data in enumerate(daily_activities):
                start_time = base_date.replace(
                    hour=random.randint(8, 17),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0
                )
                end_time = start_time + timedelta(minutes=activity_data["duration"])
                
                # Create activity data as JSON structure
                activity_json = {
                    "name": activity_data["name"],
                    "category": activity_data["category"],
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "duration_minutes": activity_data["duration"],
                    "productivity_score": activity_data["productivity"],
                    "mood": activity_data["mood"],
                    "energy_level": activity_data["energy"]
                }

                activity = ActivityLog(
                    id=uuid.uuid4(),
                    user_id=alice.id,
                    date=start_time,
                    activities=activity_json,
                    notes=f"Sample activity for testing - Day {day_offset + 1}",
                    created_at=start_time
                )
                
                db.add(activity)
                created_activities += 1
        
        print(f"✅ Created {created_activities} sample activity logs")
        
        # Create sample goals
        goals_data = [
            {
                "title": "Complete Product Roadmap",
                "description": "Finalize Q3 product roadmap with stakeholder input",
                "category": "work",
                "target_value": 100,
                "current_value": 75,
                "unit": "percent"
            },
            {
                "title": "Learn Machine Learning",
                "description": "Complete online ML course and build a project",
                "category": "learning",
                "target_value": 40,
                "current_value": 25,
                "unit": "hours"
            },
            {
                "title": "Exercise Regularly",
                "description": "Exercise at least 3 times per week",
                "category": "health",
                "target_value": 12,
                "current_value": 8,
                "unit": "sessions"
            }
        ]
        
        created_goals = 0
        for goal_data in goals_data:
            goal = Goal(
                id=uuid.uuid4(),
                user_id=alice.id,
                title=goal_data["title"],
                description=goal_data["description"],
                category=goal_data["category"],
                target_value=goal_data["target_value"],
                current_value=goal_data["current_value"],
                unit=goal_data["unit"],
                deadline=datetime.now(timezone.utc) + timedelta(days=30),
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            db.add(goal)
            created_goals += 1
        
        print(f"✅ Created {created_goals} sample goals")
        
        # Create sample AI insights
        insights_data = [
            {
                "insight_type": "productivity",
                "summary": "Peak Productivity Hours",
                "suggestions": {
                    "title": "Peak Productivity Hours",
                    "content": "Your productivity is highest between 9-11 AM and 2-4 PM. Consider scheduling important tasks during these windows.",
                    "confidence": 0.85
                }
            },
            {
                "insight_type": "schedule",
                "summary": "Meeting Optimization",
                "suggestions": {
                    "title": "Meeting Optimization",
                    "content": "You have 40% more meetings on Tuesdays and Wednesdays. Consider moving some to other days for better balance.",
                    "confidence": 0.78
                }
            },
            {
                "insight_type": "wellness",
                "summary": "Energy Management",
                "suggestions": {
                    "title": "Energy Management",
                    "content": "Your energy levels drop significantly after lunch. A 15-minute walk or brief meditation could help maintain afternoon productivity.",
                    "confidence": 0.82
                }
            }
        ]

        created_insights = 0
        for insight_data in insights_data:
            insight = AIInsight(
                id=uuid.uuid4(),
                user_id=alice.id,
                insight_type=insight_data["insight_type"],
                summary=insight_data["summary"],
                suggestions=insight_data["suggestions"],
                date=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 5)),
                generated_at=datetime.now(timezone.utc)
            )

            db.add(insight)
            created_insights += 1
        
        print(f"✅ Created {created_insights} sample AI insights")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Successfully created sample data for {alice.name}!")
        print("📊 Summary:")
        print(f"  - {created_activities} activity logs (last 7 days)")
        print(f"  - {created_goals} active goals")
        print(f"  - {created_insights} AI insights")
        print("\n🤖 Now you can test the chatbot with queries like:")
        print("  - 'What did I do yesterday?'")
        print("  - 'Show me my productivity stats'")
        print("  - 'What are my current goals?'")
        print("  - 'What insights do you have for me?'")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
