#!/usr/bin/env python3
"""
Database Migration Management Script for BookStore API

This script provides convenient commands for managing Alembic database migrations.
It can be used in development, CI/CD pipelines, and production deployments.

Usage:
    python scripts/migrate.py [command] [options]

Commands:
    status      - Show current migration status
    upgrade     - Upgrade to latest migration
    downgrade   - Downgrade by one migration
    create      - Create new migration
    history     - Show migration history
    reset       - Reset database (development only)
    validate    - Validate migration consistency

Examples:
    python scripts/migrate.py status
    python scripts/migrate.py upgrade
    python scripts/migrate.py create "Add user preferences table"
    python scripts/migrate.py downgrade
    python scripts/migrate.py history
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from bookstore.config import settings
from bookstore.database import engine


def get_alembic_config():
    """Get Alembic configuration"""
    alembic_cfg_path = project_root / "alembic.ini"
    if not alembic_cfg_path.exists():
        print(f"❌ Alembic config not found at {alembic_cfg_path}")
        sys.exit(1)
    
    alembic_cfg = Config(str(alembic_cfg_path))
    return alembic_cfg


def get_current_revision():
    """Get current database revision"""
    try:
        alembic_cfg = get_alembic_config()
        
        with engine.connect() as connection:
            # Use Alembic's migration context to get current revision
            from alembic.migration import MigrationContext
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
    except Exception as e:
        print(f"❌ Error getting current revision: {e}")
        return None


def cmd_status(args):
    """Show migration status"""
    print("📊 Database Migration Status")
    print("=" * 40)
    
    try:
        alembic_cfg = get_alembic_config()
        script = ScriptDirectory.from_config(alembic_cfg)
        
        current_rev = get_current_revision()
        head_rev = script.get_current_head()
        
        print(f"Database URL: {settings.database_url}")
        print(f"Environment: {settings.environment}")
        print(f"Current Revision: {current_rev or 'None'}")
        print(f"Head Revision: {head_rev or 'None'}")
        
        if current_rev == head_rev:
            print("✅ Database is up to date")
        elif current_rev is None:
            print("⚠️ Database has no migration version")
        else:
            print("⚠️ Database needs migration")
            
        # Show pending migrations
        if current_rev and head_rev and current_rev != head_rev:
            print("\n📋 Pending migrations:")
            command.history(alembic_cfg, verbose=False)
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        sys.exit(1)


def cmd_upgrade(args):
    """Upgrade database to latest migration"""
    print("🚀 Upgrading database...")
    
    try:
        alembic_cfg = get_alembic_config()
        
        if args.revision:
            print(f"Upgrading to revision: {args.revision}")
            command.upgrade(alembic_cfg, args.revision)
        else:
            print("Upgrading to latest revision...")
            command.upgrade(alembic_cfg, "head")
            
        print("✅ Database upgrade completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        sys.exit(1)


def cmd_downgrade(args):
    """Downgrade database"""
    if settings.is_production and not args.force:
        print("❌ Downgrade not allowed in production without --force flag")
        print("⚠️ This operation can cause data loss!")
        sys.exit(1)
    
    print("⬇️ Downgrading database...")
    
    try:
        alembic_cfg = get_alembic_config()
        
        if args.revision:
            print(f"Downgrading to revision: {args.revision}")
            command.downgrade(alembic_cfg, args.revision)
        else:
            print("Downgrading by one revision...")
            command.downgrade(alembic_cfg, "-1")
            
        print("✅ Database downgrade completed!")
        
    except Exception as e:
        print(f"❌ Error during downgrade: {e}")
        sys.exit(1)


def cmd_create(args):
    """Create new migration"""
    if not args.message:
        print("❌ Migration message is required")
        print("Usage: python scripts/migrate.py create 'Add user table'")
        sys.exit(1)
    
    print(f"📝 Creating migration: {args.message}")
    
    try:
        alembic_cfg = get_alembic_config()
        
        if args.autogenerate:
            print("🔍 Auto-generating migration from model changes...")
            command.revision(alembic_cfg, message=args.message, autogenerate=True)
        else:
            print("📄 Creating empty migration...")
            command.revision(alembic_cfg, message=args.message)
            
        print("✅ Migration created successfully!")
        print("📝 Don't forget to review and edit the migration file before applying it")
        
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        sys.exit(1)


def cmd_history(args):
    """Show migration history"""
    print("📚 Migration History")
    print("=" * 40)
    
    try:
        alembic_cfg = get_alembic_config()
        command.history(alembic_cfg, verbose=args.verbose)
        
    except Exception as e:
        print(f"❌ Error showing history: {e}")
        sys.exit(1)


def cmd_reset(args):
    """Reset database (development only)"""
    if settings.is_production:
        print("❌ Database reset not allowed in production!")
        sys.exit(1)
    
    if not args.force:
        response = input("⚠️ This will delete all data! Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Operation cancelled")
            sys.exit(0)
    
    print("🔄 Resetting database...")
    
    try:
        # Drop all tables
        from bookstore.models import Base
        Base.metadata.drop_all(bind=engine)
        print("🗑️ All tables dropped")
        
        # Run migrations from scratch
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, "head")
        print("🚀 Migrations applied")
        
        # Initialize with test data
        from bookstore.database import init_db
        init_db()
        print("📊 Test data created")
        
        print("✅ Database reset completed!")
        
    except Exception as e:
        print(f"❌ Error during reset: {e}")
        sys.exit(1)


def cmd_validate(args):
    """Validate migration consistency"""
    print("🔍 Validating migration consistency...")
    
    try:
        alembic_cfg = get_alembic_config()
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Check for multiple heads
        heads = script.get_heads()
        if len(heads) > 1:
            print(f"❌ Multiple heads detected: {heads}")
            print("💡 Use 'alembic merge' to resolve")
            sys.exit(1)
        
        # Check current revision
        current_rev = get_current_revision()
        if current_rev is None:
            print("⚠️ Database has no migration version")
            print("💡 Use 'alembic stamp head' to mark current state")
        
        # Validate migration files
        for revision in script.walk_revisions():
            try:
                script.get_revision(revision.revision)
            except Exception as e:
                print(f"❌ Invalid migration {revision.revision}: {e}")
                sys.exit(1)
        
        print("✅ Migration consistency validated!")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="BookStore API Database Migration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show migration status')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('revision', nargs='?', help='Target revision (default: head)')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', nargs='?', help='Target revision (default: -1)')
    downgrade_parser.add_argument('--force', action='store_true', help='Force downgrade in production')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new migration')
    create_parser.add_argument('message', help='Migration message')
    create_parser.add_argument('--autogenerate', action='store_true', help='Auto-generate from model changes')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show migration history')
    history_parser.add_argument('--verbose', action='store_true', help='Show detailed history')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset database (development only)')
    reset_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate migration consistency')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command
    commands = {
        'status': cmd_status,
        'upgrade': cmd_upgrade,
        'downgrade': cmd_downgrade,
        'create': cmd_create,
        'history': cmd_history,
        'reset': cmd_reset,
        'validate': cmd_validate,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"❌ Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()