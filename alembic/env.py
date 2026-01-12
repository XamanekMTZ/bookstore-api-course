"""
Alembic environment configuration for BookStore API

This module configures Alembic to work with the BookStore API database models
and settings. It integrates with the application's configuration system to
use the same database URL and settings.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the project root to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import our application modules
from bookstore.models import Base
from bookstore.config import settings

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from our application settings
# This ensures Alembic uses the same database as the application
config.set_main_option("sqlalchemy.url", settings.database_url)

# Add your model's MetaData object here for 'autogenerate' support
# This tells Alembic about all our database models
target_metadata = Base.metadata

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Enable column type comparison
        compare_server_default=True,  # Enable server default comparison
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Get database configuration from our settings
    db_config = settings.get_database_config()
    
    # Create engine configuration
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    
    # Add database-specific configuration
    if settings.database_url.startswith("sqlite"):
        # SQLite specific settings
        configuration["sqlalchemy.connect_args"] = {"check_same_thread": False}
    else:
        # PostgreSQL and other databases
        configuration["sqlalchemy.pool_size"] = str(db_config.get("pool_size", 5))
        configuration["sqlalchemy.max_overflow"] = str(db_config.get("max_overflow", 10))
        configuration["sqlalchemy.pool_timeout"] = str(db_config.get("pool_timeout", 30))
        configuration["sqlalchemy.pool_recycle"] = str(db_config.get("pool_recycle", 3600))

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Enable column type comparison
            compare_server_default=True,  # Enable server default comparison
            # Include object name in migration for better tracking
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter objects to include in migrations.
    
    This function allows us to exclude certain objects from migrations
    if needed (e.g., temporary tables, views, etc.)
    """
    # Include all objects by default
    return True


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
