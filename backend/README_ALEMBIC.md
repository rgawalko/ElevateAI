# 🗄️ Alembic Database Migrations - Quick Start

Alembic has been successfully set up for your Elevate AI project! Here's everything you need to know.

## ✅ Current Status

- **Alembic Initialized**: ✅ Ready for migrations
- **Initial Migration Created**: ✅ All current models captured
- **Database Stamped**: ✅ Marked as up-to-date
- **Azure Ready**: ✅ Environment variables configured

## 🚀 Quick Commands

### Check Current Status
```bash
python migrate.py current
```

### Create New Migration (after model changes)
```bash
python migrate.py create -m "Add new column to users"
```

### Apply Migrations
```bash
python migrate.py upgrade
```

### Check Environment
```bash
python migrate.py check
```

## 📝 Typical Workflow

1. **Make changes to your models** (e.g., add/remove columns)
2. **Create migration**: `python migrate.py create -m "Description of changes"`
3. **Review the generated migration** in `alembic/versions/`
4. **Apply migration**: `python migrate.py upgrade`

## ☁️ Azure Deployment

When deploying to Azure:

1. **Set DATABASE_URL environment variable** in Azure App Service
2. **Run migrations**: `python migrate.py upgrade`
3. **Your database will be updated** with all schema changes

## 📁 File Structure

```
backend/
├── alembic/                    # Alembic configuration
│   ├── versions/              # Migration files
│   │   └── 2025_07_31_1733-20cbe00d07c4_initial_migration_with_all_models.py
│   └── env.py                 # Environment configuration
├── alembic.ini                # Alembic settings
├── migrate.py                 # Helper script (use this!)
├── ALEMBIC_GUIDE.md          # Detailed documentation
└── README_ALEMBIC.md         # This file
```

## 🎯 Key Features

- **Auto-detection**: Automatically detects model changes
- **Environment Variables**: Uses DATABASE_URL from .env or Azure
- **Timestamped Files**: Migration files include date/time
- **Rollback Support**: Can downgrade if needed
- **Azure Compatible**: Works with Azure Database for PostgreSQL

## 🔧 Example: Adding a Column

1. **Edit your model**:
   ```python
   # In models/user.py
   class User(Base):
       # ... existing columns ...
       phone_number = Column(String(20), nullable=True)  # New column
   ```

2. **Create migration**:
   ```bash
   python migrate.py create -m "Add phone number to users"
   ```

3. **Apply migration**:
   ```bash
   python migrate.py upgrade
   ```

## 🆘 Need Help?

- **Check environment**: `python migrate.py check`
- **View history**: `python migrate.py history`
- **Read detailed guide**: See `ALEMBIC_GUIDE.md`

## 🎉 You're All Set!

Your database migration system is ready for production use. You can now:

- ✅ Make model changes safely
- ✅ Deploy to Azure with confidence
- ✅ Track all database changes
- ✅ Rollback if needed

**Happy migrating!** 🚀
