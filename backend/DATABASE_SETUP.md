# PostgreSQL Database Setup for Elevate AI

This guide will help you set up a local PostgreSQL database for the Elevate AI backend.

## Prerequisites

### 1. Install PostgreSQL

#### Windows
1. Download PostgreSQL from [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` user
4. Default port is usually `5432`

#### macOS
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql

# Or using PostgreSQL.app
# Download from https://postgresapp.com/
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Verify PostgreSQL Installation

```bash
# Check if PostgreSQL is running
psql --version

# Connect to PostgreSQL (you'll be prompted for password)
psql -U postgres -h localhost
```

## Quick Setup (Automated)

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your database credentials
# Update the DATABASE_URL line:
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/elevate_ai
```

### 3. Run Database Setup Script

```bash
python setup_database.py
```

This script will:
- ✅ Check PostgreSQL connection
- ✅ Create the `elevate_ai` database if it doesn't exist
- ✅ Initialize all required tables
- ✅ Verify the setup

### 4. Start the Backend Server

```bash
python start.py
```

## Manual Setup (Step by Step)

### 1. Create Database

Connect to PostgreSQL and create the database:

```sql
-- Connect to PostgreSQL
psql -U postgres -h localhost

-- Create database
CREATE DATABASE elevate_ai;

-- Create a dedicated user (optional but recommended)
CREATE USER elevate_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE elevate_ai TO elevate_user;

-- Exit PostgreSQL
\q
```

### 2. Configure Environment Variables

Edit `backend/.env`:

```env
# For postgres user
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/elevate_ai

# Or for dedicated user
DATABASE_URL=postgresql://elevate_user:your_secure_password@localhost:5432/elevate_ai

# Other required settings
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
DEBUG=True
```

### 3. Initialize Tables

```bash
cd backend
python -c "from database.utils import init_database; init_database()"
```

## Database Configuration Options

### Connection Pooling

The backend supports PostgreSQL connection pooling. Configure in `.env`:

```env
# Connection pool settings
DB_POOL_SIZE=10          # Number of connections to maintain
DB_MAX_OVERFLOW=20       # Additional connections when pool is full
DB_POOL_TIMEOUT=30       # Seconds to wait for connection
DB_POOL_RECYCLE=3600     # Seconds before recreating connections
```

### SSL Configuration

For production or remote databases:

```env
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require
```

## Troubleshooting

### Common Issues

#### 1. "psycopg2" Installation Error

```bash
# On Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev

# On macOS
brew install postgresql

# Then reinstall
pip install psycopg2-binary
```

#### 2. Connection Refused

- ✅ Check if PostgreSQL is running: `sudo systemctl status postgresql`
- ✅ Check if port 5432 is open: `netstat -an | grep 5432`
- ✅ Verify credentials in `.env` file

#### 3. Database Does Not Exist

```sql
-- Connect and create manually
psql -U postgres
CREATE DATABASE elevate_ai;
```

#### 4. Permission Denied

```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE elevate_ai TO your_user;
```

### Testing Connection

```bash
# Test database connection
python -c "
from database.utils import check_database_connection
if check_database_connection():
    print('✅ Database connection successful')
else:
    print('❌ Database connection failed')
"
```

## Database Schema

The backend will automatically create these tables:

- `users` - User accounts and profiles
- `user_preferences` - User settings and preferences
- `activity_logs` - User activity tracking
- `schedules` - User schedules and tasks
- `schedule_tasks` - Individual tasks within schedules
- `ai_insights` - AI-generated insights and recommendations
- `goals` - User goals and objectives
- `goal_progress` - Goal progress tracking
- `tags` - Activity and content tags
- `activity_tags` - Many-to-many relationship for activity tags
- `insight_actions` - Actions derived from AI insights

## Production Considerations

### 1. Security

```env
# Use strong passwords
DATABASE_URL=postgresql://elevate_user:very_secure_password@localhost:5432/elevate_ai

# Use environment-specific secrets
JWT_SECRET_KEY=production-grade-secret-key-256-bits-minimum
```

### 2. Performance

```env
# Optimize for production
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=50
DB_POOL_RECYCLE=7200
```

### 3. Backup

```bash
# Create backup
pg_dump -U postgres elevate_ai > elevate_ai_backup.sql

# Restore backup
psql -U postgres elevate_ai < elevate_ai_backup.sql
```

## Next Steps

After successful database setup:

1. ✅ Start the backend server: `python start.py`
2. ✅ Access API documentation: `http://localhost:8000/docs`
3. ✅ Test API endpoints using the interactive docs
4. ✅ Connect your frontend application

## Support

If you encounter issues:

1. Check the logs in the terminal output
2. Verify PostgreSQL is running and accessible
3. Ensure all environment variables are set correctly
4. Review the troubleshooting section above

For additional help, check the main project documentation or create an issue in the project repository.
