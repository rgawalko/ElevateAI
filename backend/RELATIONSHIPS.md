# 🔗 Database Relationships Documentation

This document describes the comprehensive SQLAlchemy relationships implemented in the Elevate AI backend.

## 📊 Entity Relationship Overview

```
User (Central Entity)
├── activity_logs (1:N) → ActivityLog
│   └── activity_tags (1:N) → ActivityTag
│       └── tag (N:1) → Tag
│           └── user (N:1) → User
├── ai_insights (1:N) → AIInsight
│   └── insight_actions (1:N) → InsightAction
│       └── user (N:1) → User
├── schedules (1:N) → Schedule
│   └── schedule_tasks (1:N) → ScheduleTask
│       └── user (N:1) → User
├── schedule_tasks (1:N) → ScheduleTask (direct)
├── goals (1:N) → Goal
│   └── goal_progress (1:N) → GoalProgress
│       └── user (N:1) → User
├── goal_progress (1:N) → GoalProgress (direct)
├── tags (1:N) → Tag
├── insight_actions (1:N) → InsightAction (direct)
└── preferences (1:1) → UserPreferences
```

## 🏗️ Model Relationships

### 1. **User Model** (Central Entity)
**File**: `models/user.py`

**Relationships**:
- `activity_logs` → One-to-Many with ActivityLog
- `ai_insights` → One-to-Many with AIInsight
- `schedules` → One-to-Many with Schedule
- `schedule_tasks` → One-to-Many with ScheduleTask (direct access)
- `goals` → One-to-Many with Goal
- `goal_progress` → One-to-Many with GoalProgress (direct access)
- `tags` → One-to-Many with Tag
- `insight_actions` → One-to-Many with InsightAction (direct access)
- `preferences` → One-to-One with UserPreferences

**Cascade Behavior**: All relationships use `cascade="all, delete-orphan"` for data integrity.

### 2. **Activity Tracking Models**

#### **ActivityLog Model**
**File**: `models/activity_log.py`

**Relationships**:
- `user` → Many-to-One with User
- `activity_tags` → One-to-Many with ActivityTag

**Features**:
- JSONB field for flexible activity data
- Bidirectional relationship with User
- Connected to tags via ActivityTag junction table

#### **ActivityTag Model** (Junction Table)
**File**: `models/activity_tag.py`

**Relationships**:
- `activity_log` → Many-to-One with ActivityLog
- `tag` → Many-to-One with Tag

**Constraints**:
- Unique constraint on (activity_log_id, tag_id)
- Prevents duplicate tag assignments

#### **Tag Model**
**File**: `models/activity_tag.py`

**Relationships**:
- `user` → Many-to-One with User
- `activity_tags` → One-to-Many with ActivityTag

**Constraints**:
- Unique constraint on (user_id, name)
- Prevents duplicate tag names per user

### 3. **AI Insights Models**

#### **AIInsight Model**
**File**: `models/ai_insight.py`

**Relationships**:
- `user` → Many-to-One with User
- `insight_actions` → One-to-Many with InsightAction

**Features**:
- JSONB field for flexible suggestion data
- Tracks user actions on insights

#### **InsightAction Model**
**File**: `models/insight_action.py`

**Relationships**:
- `insight` → Many-to-One with AIInsight
- `user` → Many-to-One with User

**Features**:
- Tracks user interactions with insights
- Completion status and timestamps

### 4. **Scheduling Models**

#### **Schedule Model**
**File**: `models/schedule.py`

**Relationships**:
- `user` → Many-to-One with User
- `schedule_tasks` → One-to-Many with ScheduleTask

**Features**:
- JSONB field for flexible task data
- AI generation tracking

#### **ScheduleTask Model**
**File**: `models/schedule_task.py`

**Relationships**:
- `schedule` → Many-to-One with Schedule
- `user` → Many-to-One with User (direct access)

**Features**:
- Individual task management
- Completion tracking with timestamps
- Duration calculations and overdue detection

### 5. **Goal Tracking Models**

#### **Goal Model**
**File**: `models/goal.py`

**Relationships**:
- `user` → Many-to-One with User
- `goal_progress` → One-to-Many with GoalProgress

**Features**:
- Progress percentage calculation
- Overdue detection
- Completion tracking

#### **GoalProgress Model**
**File**: `models/goal.py`

**Relationships**:
- `goal` → Many-to-One with Goal
- `user` → Many-to-One with User (direct access)

**Features**:
- Progress value tracking
- Historical progress data

### 6. **User Preferences Model**

#### **UserPreferences Model**
**File**: `models/user_preferences.py`

**Relationships**:
- `user` → One-to-One with User

**Features**:
- Comprehensive user settings
- JSONB field for custom settings
- Notification and AI preferences

## 🔧 Relationship Features

### **Cascade Behavior**
All relationships from User use `cascade="all, delete-orphan"`:
- When a user is deleted, all related data is automatically removed
- Maintains referential integrity
- Prevents orphaned records

### **Bidirectional Relationships**
All relationships are bidirectional with `back_populates`:
- Navigate from User to related entities
- Navigate from related entities back to User
- Consistent relationship access patterns

### **Direct Access Relationships**
Some models have direct relationships to User for convenience:
- `User.schedule_tasks` - Direct access to all user's tasks
- `User.goal_progress` - Direct access to all progress entries
- `User.insight_actions` - Direct access to all insight interactions

### **Junction Tables**
Many-to-many relationships use proper junction tables:
- `ActivityTag` - Links ActivityLog and Tag
- Unique constraints prevent duplicate relationships

### **One-to-One Relationships**
- `User.preferences` - Each user has exactly one preferences record
- Uses `uselist=False` for single object access

## 📋 Database Constraints

### **Unique Constraints**
1. **ActivityTag**: `(activity_log_id, tag_id)` - Prevents duplicate tag assignments
2. **Tag**: `(user_id, name)` - Prevents duplicate tag names per user
3. **UserPreferences**: `user_id` - One preferences record per user

### **Foreign Key Constraints**
All relationships use proper foreign key constraints:
- UUID foreign keys for distributed systems
- NOT NULL constraints where appropriate
- Referential integrity enforcement

## 🎯 Usage Examples

### **Accessing User's Data**
```python
# Get user with all relationships
user = session.query(User).options(
    joinedload(User.activity_logs),
    joinedload(User.schedules),
    joinedload(User.goals)
).filter(User.id == user_id).first()

# Access related data
activities = user.activity_logs
schedules = user.schedules
goals = user.goals
preferences = user.preferences
```

### **Creating Related Records**
```python
# Create user with preferences
user = User(name="John Doe", email="john@example.com")
preferences = UserPreferences(user=user, theme="dark")

session.add(user)
session.add(preferences)
session.commit()
```

### **Many-to-Many Operations**
```python
# Add tags to activity
activity = ActivityLog(user=user, activities={...})
tag1 = Tag(user=user, name="work")
tag2 = Tag(user=user, name="important")

activity_tag1 = ActivityTag(activity_log=activity, tag=tag1)
activity_tag2 = ActivityTag(activity_log=activity, tag=tag2)

session.add_all([activity, tag1, tag2, activity_tag1, activity_tag2])
session.commit()
```

## 🚀 Benefits

### **Data Integrity**
- Cascade deletes prevent orphaned records
- Foreign key constraints ensure referential integrity
- Unique constraints prevent duplicate data

### **Query Efficiency**
- Bidirectional relationships enable efficient navigation
- Direct access relationships reduce query complexity
- Proper indexing on foreign keys

### **Flexibility**
- JSONB fields for flexible data structures
- Custom settings support in UserPreferences
- Extensible relationship patterns

### **Maintainability**
- Clear relationship definitions
- Consistent naming conventions
- Comprehensive documentation

## 🧪 Testing

Run the relationship test suite:
```bash
cd backend
python test_relationships.py
```

**Test Coverage**:
- ✅ Model imports
- ✅ Relationship definitions
- ✅ Model methods and properties
- ✅ Database constraints
- ✅ Relationship diagram generation

## 📈 Performance Considerations

### **Lazy Loading**
- Relationships use lazy loading by default
- Use `joinedload()` for eager loading when needed
- Avoid N+1 query problems

### **Indexing**
- Foreign key columns are automatically indexed
- Consider additional indexes for frequently queried fields
- UUID primary keys provide good distribution

### **Query Optimization**
- Use `select_related()` equivalent (`joinedload()`) for related data
- Implement pagination for large result sets
- Consider read replicas for heavy read workloads

---

**The Elevate AI database now has a comprehensive, well-designed relationship structure that supports all application features while maintaining data integrity and performance! 🎉**
