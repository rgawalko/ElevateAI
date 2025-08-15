# Elevate AI Backend

Backend API for Elevate AI - A productivity and wellness application built with FastAPI, SQLAlchemy, and PostgreSQL.

## 🏗️ Architecture

```
backend/
├── API/
│   └── main.py              # FastAPI application entry point
├── routes/                  # API route handlers
│   ├── auth.py             # Authentication endpoints
│   ├── users.py            # User management endpoints
│   ├── activities.py       # Activity tracking endpoints
│   ├── schedules.py        # Schedule management + AI generation
│   └── insights.py         # AI insights endpoints
├── models/                  # SQLAlchemy database models
│   ├── user.py             # User model
│   ├── activity_log.py     # Activity logging model
│   ├── ai_insight.py       # AI insights model
│   └── schedule.py         # Schedule model
├── schemas/                 # Pydantic validation schemas
│   ├── user.py             # User schemas
│   ├── activity_log.py     # Activity schemas
│   ├── ai_insight.py       # Insight schemas
│   └── schedule.py         # Schedule schemas
├── database/               # Database configuration and utilities
│   ├── database.py         # SQLAlchemy setup
│   └── utils.py            # Database helper functions
└── utils/                  # Utility functions
    └── auth.py             # Authentication utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (optional - SQLite used by default for development)

### Installation

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables (optional):**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/elevate_ai"
   export SECRET_KEY="your-secret-key-here"
   ```

4. **Start the server:**
   ```bash
   python start.py
   ```

   Or manually:
   ```bash
   cd API
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API:**
   - **API Server**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication (`/api/auth`)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/verify-token` - Verify token validity

### Users (`/api/users`)
- `GET /api/users/profile` - Get user profile with statistics
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/change-password` - Change password
- `DELETE /api/users/account` - Deactivate account
- `POST /api/users/reactivate` - Reactivate account
- `GET /api/users/statistics` - Get user statistics

### Activities (`/api/activities`)
- `POST /api/activities/` - Create activity log
- `GET /api/activities/` - Get activity logs (with filtering)
- `GET /api/activities/{id}` - Get specific activity
- `PUT /api/activities/{id}` - Update activity
- `DELETE /api/activities/{id}` - Delete activity
- `GET /api/activities/stats/summary` - Get activity summary

### Schedules (`/api/schedules`)
- `POST /api/schedules/` - Create schedule
- `GET /api/schedules/` - Get schedules (with filtering)
- `GET /api/schedules/{id}` - Get specific schedule
- `PUT /api/schedules/{id}` - Update schedule
- `DELETE /api/schedules/{id}` - Delete schedule
- `POST /api/schedules/ai/generate-schedule` - **AI Schedule Generation**

### AI Insights (`/api/insights`)
- `GET /api/insights/` - Get AI insights
- `GET /api/insights/{id}` - Get specific insight
- `POST /api/insights/generate` - Generate new insights
- `DELETE /api/insights/{id}` - Delete insight
- `GET /api/insights/types/available` - Get available insight types

## 🤖 AI Schedule Generation

The AI schedule generation endpoint accepts JSON in this format:

```json
{
  "date": "2025-08-01",
  "wakeUpTime": "07:00",
  "activities": [
    { "name": "Email review", "durationMinutes": 30, "priority": 2 },
    { "name": "Team meeting", "durationMinutes": 60, "priority": 1, "timeWindow": ["09:00","11:00"] },
    { "name": "Project work", "durationMinutes": 180, "priority": 3 },
    { "name": "Gym", "durationMinutes": 45, "priority": 4 }
  ],
  "constraints": {
    "lunchBreak": true,
    "maxConsecutiveWorkHours": 4
  }
}
```

**Endpoint**: `POST /api/schedules/ai/generate-schedule`

**Response**:
```json
{
  "success": true,
  "schedule": {
    "date": "2025-08-01",
    "totalDuration": 315,
    "scheduledActivities": [...],
    "unscheduledActivities": [],
    "breaks": [...],
    "summary": {
      "totalWorkTime": 255,
      "totalBreakTime": 60,
      "totalFreeTime": 165,
      "productivityScore": 85,
      "balanceScore": 78
    }
  },
  "schedule_id": "uuid-here",
  "message": "Schedule generated successfully"
}
```

## 🗄️ Database Models

### User Model
- UUID primary key
- Profile information (name, email, avatar, bio)
- Account status (active, verified)
- User preferences (timezone, date/time format)
- Timestamps (created, updated, last login)

### Activity Log Model
- Links to User via foreign key
- JSONB field for flexible activity data
- Date and timestamp tracking
- Optional notes

### Schedule Model
- Links to User via foreign key
- JSONB field for tasks/activities
- AI generation flag
- Date-based organization

### AI Insight Model
- Links to User via foreign key
- Categorized by insight type
- JSONB field for suggestions
- Generation timestamp

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register/Login** to get access and refresh tokens
2. **Include Bearer token** in Authorization header for protected endpoints
3. **Refresh tokens** when access tokens expire

Example:
```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Use token for protected endpoints
curl -X GET "http://localhost:8000/api/users/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🧪 Testing

Run the API test suite:

```bash
# Make sure the server is running first
python start.py

# In another terminal, run tests
python test_api.py
```

## 🔧 Configuration

Environment variables:

- `DATABASE_URL` - Database connection string (default: SQLite)
- `SECRET_KEY` - JWT signing key (required for production)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: false)

## 📦 Dependencies

Key dependencies:
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and serialization
- **PyJWT** - JWT token handling
- **Uvicorn** - ASGI server
- **psycopg2** - PostgreSQL adapter

## 🚀 Production Deployment

For production deployment:

1. Set proper environment variables
2. Use PostgreSQL instead of SQLite
3. Set `DEBUG=false`
4. Use a production ASGI server like Gunicorn
5. Set up proper logging and monitoring

Example production command:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker API.main:app --bind 0.0.0.0:8000
```

## 📝 Development Notes

- The API follows RESTful conventions
- All endpoints return JSON responses
- Error handling includes proper HTTP status codes
- CORS is configured for frontend integration
- Database relationships use proper foreign keys
- Authentication is stateless using JWTs

## 🤝 Frontend Integration

The backend is designed to work seamlessly with the React frontend:

- CORS configured for `localhost:5173` (Vite) and `localhost:3000` (React)
- API responses match frontend TypeScript interfaces
- Authentication flow supports the frontend auth service
- Schedule generation endpoint matches frontend request format

---

**Ready for production use with the Elevate AI React frontend! 🎉**
