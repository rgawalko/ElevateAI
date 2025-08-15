# 🚀 Elevate AI

> **Transform your productivity with AI-powered insights and intelligent scheduling**

Elevate AI is a comprehensive productivity and wellness application that leverages artificial intelligence to help users optimize their daily routines, track activities, set and achieve goals, and gain personalized insights for enhanced productivity and well-being.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)

## 🎯 Purpose & Vision

Elevate AI addresses the modern challenge of productivity optimization by combining:
- **AI-Powered Intelligence**: Advanced algorithms for schedule optimization and pattern recognition
- **Holistic Tracking**: Comprehensive activity, mood, and energy monitoring
- **Personalized Insights**: Data-driven recommendations tailored to individual patterns
- **Goal Achievement**: Structured goal setting and progress tracking
- **Conversational AI**: Natural language assistant for productivity coaching

### Why Elevate AI?
- 📈 **Boost Productivity**: Identify peak performance hours and optimize your schedule
- 🧠 **AI-Driven Insights**: Discover hidden patterns in your behavior and productivity
- 🎯 **Goal Achievement**: Set, track, and achieve your personal and professional goals
- 💬 **Smart Assistant**: Get personalized advice through our AI chatbot
- 📊 **Data-Driven Decisions**: Make informed choices based on your activity patterns
- 🔄 **Continuous Improvement**: Adaptive learning that gets better over time

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[React + TypeScript UI]
        B[Responsive Design System]
        C[Real-time Data Visualization]
    end

    subgraph "API Layer"
        D[FastAPI Backend]
        E[RESTful Endpoints]
        F[JWT Authentication]
    end

    subgraph "Business Logic"
        G[Service Layer]
        H[AI Processing Engine]
        I[Pattern Recognition]
    end

    subgraph "Data Layer"
        J[PostgreSQL/SQLite]
        K[SQLAlchemy ORM]
        L[Alembic Migrations]
    end

    subgraph "AI Services"
        M[Azure OpenAI]
        N[Schedule Optimization]
        O[Insight Generation]
    end

    A --> D
    D --> G
    G --> H
    G --> K
    H --> M
    H --> N
    H --> O
    K --> J
```

### 🔧 Technology Stack

#### Frontend
- **React 18+** - Modern UI library with hooks and context
- **TypeScript** - Type-safe JavaScript for better development experience
- **Tailwind CSS** - Utility-first CSS framework for rapid styling
- **Vite** - Fast build tool and development server
- **Lucide React** - Beautiful, customizable icons
- **React Router** - Client-side routing and navigation

#### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Powerful ORM for database operations
- **Alembic** - Database migration management
- **Pydantic** - Data validation and serialization
- **JWT** - Secure authentication and authorization
- **Uvicorn** - ASGI server for production deployment

#### Database
- **PostgreSQL** - Production-ready relational database
- **SQLite** - Development and testing database
- **Redis** (Optional) - Caching and session storage

#### AI & Machine Learning
- **Azure OpenAI** - Advanced language models for AI features
- **Custom Algorithms** - Proprietary optimization and pattern recognition
- **Predictive Analytics** - Forecasting and trend analysis

## ✨ Core Features

### 🎨 **Smart Dashboard**
- **Personalized Overview**: Time-based greetings and contextual insights
- **Real-time Statistics**: Activity counts, productivity scores, and trends
- **Visual Analytics**: Charts, graphs, and progress indicators
- **Quick Actions**: Fast access to common tasks and features

### 📊 **Activity Tracking**
- **Comprehensive Logging**: Track activities with mood, energy, and productivity scores
- **Smart Categorization**: Automatic categorization with custom tags
- **Advanced Filtering**: Search and filter by multiple criteria
- **Export/Import**: Data portability and backup capabilities

### 🤖 **AI-Powered Schedule Generation**
- **Intelligent Optimization**: AI analyzes your patterns and preferences
- **Constraint Handling**: Respects your time blocks, breaks, and commitments
- **Priority-Based Planning**: Automatically prioritizes tasks based on importance
- **Adaptive Learning**: Improves recommendations based on your feedback

### 🎯 **Goal Management**
- **SMART Goals**: Set specific, measurable, achievable goals
- **Progress Tracking**: Visual progress indicators and milestone tracking
- **Category Organization**: Personal, professional, health, and learning goals
- **Achievement Analytics**: Success patterns and completion insights

### 🧠 **AI Insights & Analytics**
- **Pattern Recognition**: Discover productivity patterns and trends
- **Predictive Analytics**: Forecast energy levels and optimal work times
- **Personalized Recommendations**: Tailored advice for improvement
- **Correlation Analysis**: Understand relationships between activities and outcomes

### 💬 **Conversational AI Assistant**
- **Natural Language Processing**: Chat naturally about productivity and goals
- **Contextual Awareness**: Understands your data and current situation
- **Productivity Coaching**: Personalized advice and motivation
- **Multi-turn Conversations**: Maintains context across interactions

### 🔐 **Security & Privacy**
- **JWT Authentication**: Secure token-based authentication
- **Data Encryption**: Protected user data and communications
- **Privacy Controls**: User control over data sharing and AI processing
- **Secure API**: Rate limiting and input validation

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Lucide React** for icons
- Modern React patterns (hooks, context, etc.)

### Backend
- **FastAPI** (Python) for high-performance API
- **SQLAlchemy ORM** with PostgreSQL/SQLite
- **JWT authentication** with secure token handling
- **Pydantic** for data validation
- **Service layer** architecture for business logic
- **AI/ML integration** for insights and scheduling

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- PostgreSQL (optional, SQLite for development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd elevate-ai
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Frontend will be available at `http://localhost:5173`

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python start.py
   ```
   Backend will be available at `http://localhost:8000`
   API docs at `http://localhost:8000/docs`

### Environment Variables

Create a `.env` file in the root directory (use `.env.example` as template):

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/elevate_ai
# Or use SQLite for development:
# DATABASE_URL=sqlite:///./elevate_ai.db

# JWT Authentication
SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Azure OpenAI (Optional - for AI features)
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# API Configuration
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

### Database Setup

1. **For SQLite (Development)**:
   ```bash
   cd backend
   python setup_database.py
   ```

2. **For PostgreSQL (Production)**:
   ```bash
   # Create database
   createdb elevate_ai

   # Run migrations
   cd backend
   alembic upgrade head
   ```

## 📖 Usage Guide

### Getting Started with Elevate AI

1. **Create Your Account**
   - Register with email and password
   - Complete your profile setup
   - Set your timezone and preferences

2. **Start Activity Tracking**
   - Log your first activity with mood and energy levels
   - Use categories to organize your activities
   - Add custom tags for better organization

3. **Generate Your First AI Schedule**
   - Navigate to Schedule Creator
   - Add your planned activities with durations
   - Set constraints (lunch breaks, work hours)
   - Let AI optimize your schedule

4. **Set Goals**
   - Create SMART goals with deadlines
   - Track progress with visual indicators
   - Get AI insights on goal achievement

5. **Explore AI Insights**
   - View productivity patterns
   - Discover peak performance hours
   - Get personalized recommendations

6. **Chat with AI Assistant**
   - Ask questions about productivity
   - Get scheduling advice
   - Receive motivational coaching

### Key Workflows

#### 📊 **Daily Activity Logging**
```
Dashboard → Activities → Log Activity → Fill Details → Save
```
- Track what you did, when, and how you felt
- Rate productivity, mood, and energy levels
- Add relevant tags and categories

#### 🤖 **AI Schedule Generation**
```
Schedule → Create Schedule → Add Activities → Set Constraints → Generate AI Schedule
```
- Input your planned activities
- Set time constraints and preferences
- Let AI create an optimized schedule
- Review and adjust as needed

#### 🎯 **Goal Management**
```
Goals → Create Goal → Set Details → Track Progress → Review Insights
```
- Define specific, measurable goals
- Set realistic deadlines
- Monitor progress regularly
- Adjust strategies based on insights

## 📚 Documentation

- **[Frontend README](frontend/README.md)** - Frontend-specific documentation
- **[Backend README](backend/README.md)** - Backend-specific documentation
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when backend is running)
- **[Service Layer](backend/SERVICES.md)** - Business logic documentation
- **[Database Setup](backend/DATABASE_SETUP.md)** - Database configuration guide
- **[Features Summary](FEATURES_SUMMARY.md)** - Comprehensive feature overview
- **[AI Features](AI_FEATURES_SUMMARY.md)** - Detailed AI capabilities documentation

## 🔗 API Endpoints

### 🔐 Authentication (`/api/auth`)
- `POST /register` - User registration with email/password
- `POST /login` - User authentication and token generation
- `GET /me` - Get current authenticated user profile
- `POST /refresh` - Refresh JWT access token
- `POST /logout` - Logout and invalidate token

### 👤 Users (`/api/users`)
- `GET /profile` - Get detailed user profile
- `PUT /profile` - Update user profile information
- `GET /preferences` - Get user preferences
- `PUT /preferences` - Update user preferences

### 📊 Activities (`/api/activities`)
- `GET /` - Get user activities with filtering and pagination
- `POST /` - Create new activity log entry
- `GET /{id}` - Get specific activity details
- `PUT /{id}` - Update existing activity
- `DELETE /{id}` - Delete activity entry
- `GET /stats` - Get activity statistics and summaries

### 📅 Schedules (`/api/schedules`)
- `GET /` - Get user schedules with date filtering
- `POST /` - Create new schedule manually
- `GET /{id}` - Get specific schedule details
- `PUT /{id}` - Update existing schedule
- `DELETE /{id}` - Delete schedule
- `POST /ai/generate-schedule` - **🤖 AI-powered schedule generation**
- `POST /{id}/optimize` - Optimize existing schedule with AI

### 🎯 Goals (`/api/goals`)
- `GET /` - Get user goals with filtering options
- `POST /` - Create new goal with progress tracking
- `GET /{id}` - Get specific goal details
- `PUT /{id}` - Update goal information and progress
- `DELETE /{id}` - Delete goal
- `GET /stats` - Get goal completion statistics

### 🧠 Insights (`/api/insights`)
- `GET /` - Get AI-generated insights for user
- `POST /generate` - Generate new insights based on recent data
- `GET /productivity` - Get productivity pattern insights
- `GET /recommendations` - Get personalized recommendations

### 💬 Chatbot (`/api/chatbot`)
- `POST /chat` - Send message to AI assistant
- `GET /conversations` - Get chat conversation history
- `DELETE /conversations` - Clear chat history

### 🏠 Dashboard (`/api/home`)
- `GET /dashboard` - Get comprehensive dashboard data
- `GET /stats` - Get overview statistics
- `GET /recent-activities` - Get recent activity summary

## 🏗️ Project Structure

```
elevate-ai/
├── 📁 frontend/                    # React + TypeScript Frontend
│   ├── 📁 src/
│   │   ├── 📁 components/         # Reusable UI components
│   │   ├── 📁 pages/             # Page components (Dashboard, Activities, etc.)
│   │   ├── 📁 services/          # API services and data fetching
│   │   ├── 📁 types/             # TypeScript type definitions
│   │   ├── 📁 utils/             # Utility functions and helpers
│   │   └── 📁 hooks/             # Custom React hooks
│   ├── 📄 package.json           # Frontend dependencies
│   └── 📄 vite.config.ts         # Vite configuration
│
├── 📁 backend/                     # FastAPI + Python Backend
│   ├── 📁 API/                   # FastAPI application entry point
│   ├── 📁 models/                # SQLAlchemy database models
│   ├── 📁 routes/                # API route handlers
│   ├── 📁 services/              # Business logic layer
│   ├── 📁 schemas/               # Pydantic validation schemas
│   ├── 📁 database/              # Database configuration and utilities
│   ├── 📁 utils/                 # Backend utility functions
│   ├── 📁 alembic/               # Database migration management
│   └── 📄 requirements.txt       # Python dependencies
│
├── 📄 .env.example               # Environment variables template
├── 📄 .gitignore                 # Git ignore rules
├── 📄 README.md                  # This file
├── 📄 FEATURES_SUMMARY.md        # Comprehensive feature documentation
└── 📄 AI_FEATURES_SUMMARY.md     # AI capabilities documentation
```

## 🧪 Development

### Frontend Development
```bash
cd frontend
npm install          # Install dependencies
npm run dev          # Start development server (http://localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt  # Install dependencies
python start.py                  # Start development server (http://localhost:8000)
python test_api.py              # Run API tests
alembic upgrade head            # Run database migrations
alembic revision --autogenerate # Generate new migration
```

### Development Workflow
1. **Start Backend**: `cd backend && python start.py`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Access Application**: Frontend at `http://localhost:5173`, API docs at `http://localhost:8000/docs`

## 🚀 Deployment

### Production Deployment

#### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting service
```

#### Backend (Docker)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "API.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Environment Variables for Production
```env
DATABASE_URL=postgresql://user:password@host:5432/elevate_ai
SECRET_KEY=your-production-secret-key
AZURE_OPENAI_API_KEY=your-production-api-key
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.com
```

## 🎯 AI Schedule Generation Example

Send a POST request to `/api/schedules/ai/generate-schedule`:

```json
{
  "date": "2025-08-15",
  "wakeUpTime": "07:00",
  "activities": [
    {
      "name": "Email review",
      "durationMinutes": 30,
      "priority": 2,
      "category": "work"
    },
    {
      "name": "Team meeting",
      "durationMinutes": 60,
      "priority": 1,
      "category": "work"
    },
    {
      "name": "Workout",
      "durationMinutes": 45,
      "priority": 2,
      "category": "exercise"
    }
  ],
  "constraints": {
    "lunchBreak": true,
    "lunchTime": "12:00",
    "maxConsecutiveWorkHours": 4,
    "preferredWorkStartTime": "09:00",
    "preferredWorkEndTime": "17:00"
  }
}
```

**Response**: Optimized schedule with time slots, explanations, and productivity insights.

## 🤝 Contributing

We welcome contributions to Elevate AI! Here's how you can help:

### Development Setup
1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/elevate-ai.git
   cd elevate-ai
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Set up development environment**
   ```bash
   # Backend setup
   cd backend
   pip install -r requirements.txt
   python setup_database.py

   # Frontend setup
   cd ../frontend
   npm install
   ```

4. **Make your changes and test**
   ```bash
   # Run backend tests
   cd backend && python test_api.py

   # Run frontend linting
   cd frontend && npm run lint
   ```

5. **Commit and push**
   ```bash
   git add .
   git commit -m 'Add amazing feature: description of changes'
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Provide a clear description of changes
   - Include screenshots for UI changes
   - Reference any related issues

### Contribution Guidelines
- Follow existing code style and conventions
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

### Areas for Contribution
- 🐛 **Bug Fixes**: Report and fix issues
- ✨ **New Features**: Implement new functionality
- 📚 **Documentation**: Improve docs and examples
- 🎨 **UI/UX**: Enhance user interface and experience
- 🧪 **Testing**: Add tests and improve coverage
- 🚀 **Performance**: Optimize application performance

## 🐛 Issues & Support

- **Bug Reports**: Use GitHub Issues with detailed reproduction steps
- **Feature Requests**: Describe the feature and its use case
- **Questions**: Check existing issues or start a discussion
- **Security Issues**: Email security concerns privately

## 📊 Project Status

- ✅ **Core Features**: Activity tracking, goal management, basic AI
- ✅ **AI Integration**: Azure OpenAI integration for schedule optimization
- ✅ **Authentication**: JWT-based user authentication
- ✅ **Database**: PostgreSQL/SQLite support with migrations
- 🚧 **Advanced AI**: Enhanced pattern recognition and predictions
- 🚧 **Mobile App**: React Native mobile application
- 🚧 **Team Features**: Collaboration and team productivity tools

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Elevate AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Acknowledgments

- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance Python web framework
- **[React](https://reactjs.org/)** - Modern frontend library
- **[Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)** - AI-powered features
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit and ORM
- **[Lucide](https://lucide.dev/)** - Beautiful icon library
- **Open Source Community** - For inspiration and best practices

## 🌟 Star History

If you find Elevate AI helpful, please consider giving it a star! ⭐

---

<div align="center">

**Built with ❤️ for productivity enthusiasts**

[🌐 Website](https://elevate-ai.com) • [📧 Contact](mailto:contact@elevate-ai.com) • [🐦 Twitter](https://twitter.com/elevateai)

</div>
