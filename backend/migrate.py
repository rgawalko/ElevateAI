#!/usr/bin/env python3
"""
Database migration management script for Elevate AI.
This script provides convenient commands for managing Alembic migrations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[*] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"[+] {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] {description} failed!")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def create_migration(message):
    """Create a new migration"""
    if not message:
        message = input("Enter migration message: ").strip()
    
    if not message:
        print("❌ Migration message is required!")
        return False
    
    command = f"alembic revision --autogenerate -m \"{message}\""
    return run_command(command, f"Creating migration: {message}")

def upgrade_database(revision="head"):
    """Upgrade database to a specific revision"""
    command = f"alembic upgrade {revision}"
    return run_command(command, f"Upgrading database to {revision}")

def downgrade_database(revision):
    """Downgrade database to a specific revision"""
    if not revision:
        print("❌ Revision is required for downgrade!")
        return False
    
    command = f"alembic downgrade {revision}"
    return run_command(command, f"Downgrading database to {revision}")

def show_current_revision():
    """Show current database revision"""
    command = "alembic current"
    return run_command(command, "Showing current database revision")

def show_migration_history():
    """Show migration history"""
    command = "alembic history --verbose"
    return run_command(command, "Showing migration history")

def show_pending_migrations():
    """Show pending migrations"""
    command = "alembic show head"
    return run_command(command, "Showing pending migrations")

def stamp_database(revision="head"):
    """Stamp database with a specific revision (without running migrations)"""
    command = f"alembic stamp {revision}"
    return run_command(command, f"Stamping database with revision {revision}")

def init_database():
    """Initialize database with current schema (for existing databases)"""
    print("[*] Initializing database with current schema...")
    print("This will stamp the database as up-to-date without running migrations.")
    print("Use this only if your database already has the current schema.")

    confirm = input("Are you sure you want to stamp the database as 'head'? (y/N): ").strip().lower()
    if confirm == 'y':
        return stamp_database("head")
    else:
        print("[-] Database initialization cancelled.")
        return False

def check_environment():
    """Check if environment is properly configured"""
    print("[*] Checking environment configuration...")

    # Check if alembic directory exists
    if not Path("alembic").exists():
        print("[-] Alembic directory not found! Run 'alembic init alembic' first.")
        return False

    # Check if models can be imported
    try:
        from models import User, Chat, Message
        print("[+] Models imported successfully")
    except ImportError as e:
        print(f"[-] Failed to import models: {e}")
        return False

    # Check database connection
    try:
        from database.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[+] Database connection successful")
    except Exception as e:
        print(f"[-] Database connection failed: {e}")
        return False

    print("[+] Environment check passed!")
    return True

def main():
    parser = argparse.ArgumentParser(description="Database migration management for Elevate AI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create migration
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('-m', '--message', help='Migration message')
    
    # Upgrade database
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('revision', nargs='?', default='head', help='Target revision (default: head)')
    
    # Downgrade database
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', help='Target revision')
    
    # Show current revision
    subparsers.add_parser('current', help='Show current database revision')
    
    # Show history
    subparsers.add_parser('history', help='Show migration history')
    
    # Show pending
    subparsers.add_parser('pending', help='Show pending migrations')
    
    # Stamp database
    stamp_parser = subparsers.add_parser('stamp', help='Stamp database with revision')
    stamp_parser.add_argument('revision', nargs='?', default='head', help='Target revision (default: head)')
    
    # Initialize database
    subparsers.add_parser('init', help='Initialize existing database (stamp as head)')
    
    # Check environment
    subparsers.add_parser('check', help='Check environment configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    if args.command == 'create':
        create_migration(args.message)
    elif args.command == 'upgrade':
        upgrade_database(args.revision)
    elif args.command == 'downgrade':
        downgrade_database(args.revision)
    elif args.command == 'current':
        show_current_revision()
    elif args.command == 'history':
        show_migration_history()
    elif args.command == 'pending':
        show_pending_migrations()
    elif args.command == 'stamp':
        stamp_database(args.revision)
    elif args.command == 'init':
        init_database()
    elif args.command == 'check':
        check_environment()

if __name__ == "__main__":
    main()
