# 🗄️ Alembic Database Migration Guide

This guide covers how to use Alembic for database migrations in the Elevate AI project.

## 📋 Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Common Commands](#common-commands)
- [Migration Workflow](#migration-workflow)
- [Azure Deployment](#azure-deployment)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

Alembic is a database migration tool for SQLAlchemy. It allows you to:
- Track database schema changes over time
- Apply incremental updates to your database
- Rollback changes if needed
- Deploy schema changes to production environments like Azure

## 🔧 Setup

Alembic has been configured for your project with the following structure:

```
backend/
├── alembic/                    # Alembic configuration directory
│   ├── versions/              # Migration files
│   ├── env.py                 # Environment configuration
│   └── script.py.mako         # Migration template
├── alembic.ini                # Alembic configuration file
└── migrate.py                 # Helper script for common operations
```

### Configuration Features

- ✅ **Environment Variables**: Automatically loads DATABASE_URL from .env
- ✅ **Model Auto-discovery**: Imports all your SQLAlchemy models
- ✅ **Timestamped Migrations**: Files include date/time for easy tracking
- ✅ **Azure Compatible**: Works with PostgreSQL and Azure Database

## 🚀 Common Commands

Use the `migrate.py` helper script for easy migration management:

### Check Environment
```bash
python migrate.py check
```
Verifies that models can be imported and database connection works.

### Create a New Migration
```bash
python migrate.py create -m "Add new column to users table"
```
Creates a new migration file with auto-generated changes.

### Apply Migrations
```bash
python migrate.py upgrade
```
Applies all pending migrations to the database.

### Rollback Migrations
```bash
python migrate.py downgrade <revision>
```
Rolls back to a specific revision.

### Show Current Status
```bash
python migrate.py current
```
Shows the current database revision.

### Show Migration History
```bash
python migrate.py history
```
Shows all migrations and their status.

### Initialize Existing Database
```bash
python migrate.py init
```
Stamps an existing database as up-to-date (use when database already has current schema).

## 📝 Migration Workflow

### 1. Making Model Changes

When you modify your SQLAlchemy models:

1. **Edit your model files** (e.g., `models/user.py`)
2. **Create a migration**:
   ```bash
   python migrate.py create -m "Descriptive message about changes"
   ```
3. **Review the generated migration** in `alembic/versions/`
4. **Apply the migration**:
   ```bash
   python migrate.py upgrade
   ```

### 2. Example: Adding a New Column

1. **Add column to model**:
   ```python
   # In models/user.py
   class User(Base):
       # ... existing columns ...
       phone_number = Column(String(20), nullable=True)
   ```

2. **Create migration**:
   ```bash
   python migrate.py create -m "Add phone_number to users"
   ```

3. **Review generated migration**:
   ```python
   def upgrade() -> None:
       op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))

   def downgrade() -> None:
       op.drop_column('users', 'phone_number')
   ```

4. **Apply migration**:
   ```bash
   python migrate.py upgrade
   ```

## ☁️ Azure Deployment

### Setting Up for Azure

1. **Set Azure Database URL**:
   ```bash
   export DATABASE_URL="postgresql://username:password@server.postgres.database.azure.com:5432/database?sslmode=require"
   ```

2. **Run migrations on Azure**:
   ```bash
   python migrate.py upgrade
   ```

### Azure Database for PostgreSQL

When deploying to Azure Database for PostgreSQL:

1. **Connection String Format**:
   ```
   postgresql://username%40servername:password@servername.postgres.database.azure.com:5432/database?sslmode=require
   ```

2. **Environment Variables in Azure**:
   - Set `DATABASE_URL` in your Azure App Service configuration
   - Alembic will automatically use this URL

3. **Migration in CI/CD Pipeline**:
   ```yaml
   # Example Azure DevOps pipeline step
   - script: |
       cd backend
       python migrate.py upgrade
     displayName: 'Run Database Migrations'
   ```

## 🔍 Troubleshooting

### Common Issues

#### 1. "No such revision" Error
```bash
# Check current revision
python migrate.py current

# Check migration history
python migrate.py history

# If database is out of sync, stamp with correct revision
python migrate.py stamp <revision_id>
```

#### 2. "Target database is not up to date" Error
```bash
# Apply pending migrations
python migrate.py upgrade
```

#### 3. Model Import Errors
```bash
# Check if models can be imported
python migrate.py check

# If imports fail, check your Python path and model definitions
```

#### 4. Database Connection Issues
- Verify DATABASE_URL in .env file
- Check database server is running
- Verify credentials and permissions

### Manual Alembic Commands

If you need to use Alembic directly:

```bash
# Create migration
alembic revision --autogenerate -m "message"

# Apply migrations
alembic upgrade head

# Show current revision
alembic current

# Show history
alembic history --verbose

# Downgrade
alembic downgrade -1
```

## 📚 Best Practices

1. **Always review generated migrations** before applying them
2. **Use descriptive migration messages** that explain what changed
3. **Test migrations on a copy of production data** before deploying
4. **Keep migrations small and focused** on specific changes
5. **Never edit applied migrations** - create new ones instead
6. **Backup your database** before running migrations in production

## 🎉 Current Status

Your database is now set up with Alembic and ready for migrations:

- ✅ **Initial migration created**: Captures current schema
- ✅ **Database stamped**: Marked as up-to-date
- ✅ **Ready for Azure**: Environment variables configured
- ✅ **Helper script available**: Use `migrate.py` for easy management

You can now safely make model changes and create migrations for deployment to Azure!
