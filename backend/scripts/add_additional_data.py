#!/usr/bin/env python3
"""
Script to add additional data types like chat messages, goal progress, and more detailed insights
"""

import sys
import os
import uuid
import random
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database.database import SessionLocal
from models.user import User
from models.goal import Goal, GoalProgress
from models.chat import Chat, Message

def add_chat_conversations():
    """Add realistic chat conversations for each user"""
    
    db = SessionLocal()
    
    try:
        print("💬 Adding chat conversations...")
        
        users = db.query(User).all()
        
        # Sample chat conversations by user role
        chat_templates = {
            "Product Manager": [
                {"user": "What are my productivity insights for this week?", "assistant": "Based on your activity data, you've been most productive during 9-11 AM with an average productivity score of 8.2/10. Your energy tends to dip after lunch around 2 PM. I recommend scheduling your most important product strategy work in the morning and lighter tasks like email in the afternoon."},
                {"user": "How are my goals progressing?", "assistant": "You're making great progress! Your Q4 Product Roadmap is 75% complete and on track. The User Satisfaction Score goal is at 4.2/4.5 - you're very close to your target. I suggest focusing on the user feedback from the recent surveys to push it over the finish line."},
                {"user": "Can you help me plan tomorrow's schedule?", "assistant": "Absolutely! Based on your peak productivity hours, I recommend starting with 2 hours of deep work on the product roadmap from 9-11 AM, followed by stakeholder meetings in the afternoon when your energy is good for collaboration. Would you like me to create a detailed schedule?"},
            ],
            "Software Engineer": [
                {"user": "Show me my coding productivity patterns", "assistant": "Your coding sessions are most effective in the morning, with an average focus time of 2.5 hours. You complete features 40% faster when you start coding before 10 AM. Bug fixing seems to work better for you in the afternoon. Your code review quality is consistently high throughout the day."},
                {"user": "What should I focus on to improve my skills?", "assistant": "Based on your learning activities, you're making excellent progress with React (35/60 hours completed). I notice you learn best through hands-on projects. Consider building a side project to reinforce the advanced patterns you're studying. Your system design goal could benefit from more consistent daily practice."},
                {"user": "Help me optimize my development workflow", "assistant": "I've noticed you're most productive with 90-minute coding blocks followed by 15-minute breaks. Your debugging sessions are 30% more successful in the afternoon. Try batching code reviews in the morning when your attention to detail is highest."},
            ],
            "Marketing Director": [
                {"user": "How effective are my marketing campaigns?", "assistant": "Your creative work peaks on Tuesdays and Wednesdays - that's when you produce your best content. Campaign planning sessions are most effective in the morning. Your lead generation goal is progressing well at 100/140. I recommend scheduling content creation mid-week for maximum impact."},
                {"user": "What insights do you have about my work patterns?", "assistant": "You have excellent creative energy management! Your most innovative ideas come during uninterrupted 2-3 hour blocks. Analytics review is most effective when done in focused 45-minute sessions. Your email marketing improvements are showing great results - open rates have increased from 22% to 26%."},
                {"user": "Can you suggest improvements for my daily routine?", "assistant": "Based on your activity patterns, try protecting your Tuesday-Wednesday creative blocks from meetings. Your mindfulness practice is having a positive impact - days with meditation show 25% higher creativity scores. Consider extending your morning planning time to 45 minutes."},
            ],
            "UX Designer": [
                {"user": "How can I improve my design workflow?", "assistant": "Your design flow state is strongest during 2-3 hour uninterrupted blocks, typically achieving 40% better design quality. User interviews are most insightful when conducted in the morning. Your design system progress is excellent at 70% completion. I recommend protecting your afternoon design time from interruptions."},
                {"user": "What patterns do you see in my creative work?", "assistant": "You enter flow state most easily on Tuesdays and Thursdays. Wireframing sessions are 50% more productive when preceded by user research review. Your usability testing insights are most actionable when analyzed within 24 hours of the session. Creative brainstorming works best for you in collaborative morning sessions."},
                {"user": "Help me balance user research and design time", "assistant": "Your user research analysis is most thorough in the morning (8.5/10 average quality vs 7.2/10 in afternoon). Design execution flows better in the afternoon when you're in a more relaxed creative state. Try scheduling research in the morning and design work after lunch for optimal results."},
            ],
            "Data Scientist": [
                {"user": "Analyze my data science productivity", "assistant": "Your model training is most efficient when started in the afternoon - 30% faster completion times. Data analysis accuracy peaks in the morning with 95% accuracy vs 87% in the afternoon. Your algorithm optimization sessions show best results during 2-3 hour focused blocks. Statistical modeling is most effective on Tuesdays and Wednesdays."},
                {"user": "How are my machine learning projects progressing?", "assistant": "Excellent progress! You've deployed 1/3 ML models to production and improved model accuracy by 8/15%. Your deep learning course completion is at 3/5 courses. I notice your learning velocity increases when you combine theoretical study with practical implementation. Consider more hands-on projects."},
                {"user": "What's the best way to structure my research time?", "assistant": "Your research paper reading is most effective in 60-90 minute focused sessions, preferably in the morning. Experiment design benefits from collaborative discussion - your solo vs team sessions show 40% better methodology when discussed with peers. Data pipeline development works best in the afternoon when you're in implementation mode."},
            ]
        }
        
        created_chats = 0
        created_messages = 0
        
        for user in users:
            role = get_user_role(user.name)
            conversations = chat_templates.get(role, chat_templates["Product Manager"])
            
            # Create 2-3 chat conversations per user
            for i in range(random.randint(2, 3)):
                chat_created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14))
                chat = Chat(
                    user_id=user.id,
                    title=f"Productivity Discussion {i+1}",
                    created_at=chat_created_at,
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(chat)
                db.flush()
                created_chats += 1

                # Add 2-4 message pairs per chat
                conversation = random.choice(conversations)

                # User message
                user_message = Message(
                    chat_id=chat.chat_id,
                    sender_id=user.id,
                    sender_type="user",
                    content=conversation["user"],
                    sent_at=chat_created_at
                )
                db.add(user_message)
                created_messages += 1

                # Assistant response
                assistant_message = Message(
                    chat_id=chat.chat_id,
                    sender_id=None,  # AI messages have no sender_id
                    sender_type="assistant",
                    content=conversation["assistant"],
                    sent_at=chat_created_at + timedelta(seconds=30)
                )
                db.add(assistant_message)
                created_messages += 1
        
        print(f"    ✅ Created {created_chats} chat conversations")
        print(f"    ✅ Created {created_messages} chat messages")
        
        # Add goal progress entries
        print("📈 Adding goal progress entries...")
        
        goals = db.query(Goal).filter(Goal.is_active == True).all()
        created_progress = 0
        
        for goal in goals:
            # Create 3-7 progress entries over the past month
            num_entries = random.randint(3, 7)
            
            for i in range(num_entries):
                days_ago = random.randint(1, 30)
                progress_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
                
                # Calculate realistic progress value
                progress_factor = (30 - days_ago) / 30  # More recent = more progress
                base_progress = goal.current_value * progress_factor
                variation = random.uniform(-0.1, 0.1) * base_progress
                progress_value = max(0, base_progress + variation)
                
                progress_entry = GoalProgress(
                    goal_id=goal.id,
                    user_id=goal.user_id,
                    value=progress_value,
                    notes=f"Progress update: {progress_value:.1f} {goal.unit}",
                    date=progress_date
                )
                db.add(progress_entry)
                created_progress += 1
        
        print(f"    ✅ Created {created_progress} goal progress entries")
        
        db.commit()
        print("✅ Successfully added additional data!")
        
    except Exception as e:
        print(f"❌ Error adding additional data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_user_role(name):
    """Map user names to their roles"""
    role_mapping = {
        "Alice Johnson": "Product Manager",
        "Bob Smith": "Software Engineer", 
        "Carol Davis": "Marketing Director",
        "David Wilson": "UX Designer",
        "Emma Brown": "Data Scientist"
    }
    return role_mapping.get(name, "Product Manager")

def show_data_summary():
    """Show a summary of all data in the database"""
    
    db = SessionLocal()
    
    try:
        print("\n📊 DATABASE SUMMARY")
        print("=" * 50)
        
        from models.activity_log import ActivityLog
        from models.ai_insight import AIInsight
        from models.schedule import Schedule
        from models.chat import Chat, Message
        
        users = db.query(User).all()
        print(f"👥 Users: {len(users)}")
        
        for user in users:
            print(f"\n👤 {user.name} ({user.email})")
            
            # Count data for this user
            activities = db.query(ActivityLog).filter(ActivityLog.user_id == user.id).count()
            goals = db.query(Goal).filter(Goal.user_id == user.id).count()
            insights = db.query(AIInsight).filter(AIInsight.user_id == user.id).count()
            schedules = db.query(Schedule).filter(Schedule.user_id == user.id).count()
            chats = db.query(Chat).filter(Chat.user_id == user.id).count()
            
            print(f"  📝 Activity Logs: {activities}")
            print(f"  🎯 Goals: {goals}")
            print(f"  🧠 AI Insights: {insights}")
            print(f"  📅 Schedules: {schedules}")
            print(f"  💬 Chat Conversations: {chats}")
        
        # Overall totals
        total_activities = db.query(ActivityLog).count()
        total_goals = db.query(Goal).count()
        total_insights = db.query(AIInsight).count()
        total_schedules = db.query(Schedule).count()
        total_chats = db.query(Chat).count()
        total_messages = db.query(Message).count()
        total_progress = db.query(GoalProgress).count()
        
        print(f"\n📈 TOTALS:")
        print(f"  📝 Total Activity Logs: {total_activities}")
        print(f"  🎯 Total Goals: {total_goals}")
        print(f"  📊 Total Goal Progress Entries: {total_progress}")
        print(f"  🧠 Total AI Insights: {total_insights}")
        print(f"  📅 Total Schedules: {total_schedules}")
        print(f"  💬 Total Chat Conversations: {total_chats}")
        print(f"  💭 Total Chat Messages: {total_messages}")
        
        print(f"\n🎉 Database is fully populated with comprehensive data!")
        print("🔗 You can now test the application with rich, realistic data.")
        
    except Exception as e:
        print(f"❌ Error showing summary: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_chat_conversations()
    show_data_summary()
