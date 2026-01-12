"""
Database configuration using new settings system with Alembic migrations
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .models import Base
from .config import settings


def create_database_engine():
    """Create database engine with configuration"""
    db_config = settings.get_database_config()
    
    # SQLite settings
    if db_config["url"].startswith("sqlite"):
        engine = create_engine(
            db_config["url"],
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=db_config["echo"]
        )
    else:
        # PostgreSQL and other DB settings
        engine = create_engine(
            db_config["url"],
            echo=db_config["echo"],
            pool_size=db_config["pool_size"],
            max_overflow=db_config["max_overflow"],
            pool_timeout=db_config["pool_timeout"],
            pool_recycle=db_config["pool_recycle"]
        )
    
    return engine


# Create engine and session
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """
    Create all tables (legacy method - use Alembic migrations instead)
    
    This method is kept for backward compatibility but should not be used
    in production. Use 'alembic upgrade head' instead.
    """
    Base.metadata.create_all(bind=engine)


def run_migrations():
    """
    Run Alembic migrations programmatically
    
    This function runs Alembic migrations from within the application.
    It's useful for automated deployments and testing.
    """
    try:
        from alembic.config import Config
        from alembic import command
        
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the project root
        project_root = os.path.dirname(current_dir)
        # Path to alembic.ini
        alembic_cfg_path = os.path.join(project_root, "alembic.ini")
        
        if not os.path.exists(alembic_cfg_path):
            print(f"Warning: Alembic config not found at {alembic_cfg_path}")
            print("Falling back to create_all() method")
            create_tables()
            return
        
        # Create Alembic configuration
        alembic_cfg = Config(alembic_cfg_path)
        
        # Run migrations to the latest version
        print("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Database migrations completed successfully!")
        
    except ImportError:
        print("Alembic not installed, falling back to create_all() method")
        create_tables()
    except Exception as e:
        print(f"Error running migrations: {e}")
        print("Falling back to create_all() method")
        create_tables()


def get_migration_info():
    """
    Get current migration information
    
    Returns information about the current database migration state.
    """
    try:
        from alembic.config import Config
        from alembic import command
        from alembic.runtime.environment import EnvironmentContext
        from alembic.script import ScriptDirectory
        import io
        
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        alembic_cfg_path = os.path.join(project_root, "alembic.ini")
        
        if not os.path.exists(alembic_cfg_path):
            return {"status": "no_alembic", "message": "Alembic not configured"}
        
        alembic_cfg = Config(alembic_cfg_path)
        script = ScriptDirectory.from_config(alembic_cfg)
        
        # Capture current revision
        def get_current_revision():
            with engine.connect() as connection:
                context = EnvironmentContext(alembic_cfg, script)
                context.configure(connection=connection)
                return context.get_current_revision()
        
        current_rev = get_current_revision()
        head_rev = script.get_current_head()
        
        return {
            "status": "ok",
            "current_revision": current_rev,
            "head_revision": head_rev,
            "up_to_date": current_rev == head_rev
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize DB with migrations and test data"""
    from .models import User, Author, Genre, Book
    from .auth import get_password_hash
    
    # Run migrations instead of create_all()
    run_migrations()
    
    # Skip test data creation in production
    if settings.is_production:
        print("Production environment - skipping test data creation")
        return
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already initialized")
            return
        
        print("Creating test data...")
        
        # Create superuser
        admin_user = User(
            email="admin@bookstore.com",
            username="admin",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        
        # Create regular user only in development
        if settings.is_development:
            regular_user = User(
                email="user@example.com",
                username="testuser",
                full_name="Test User",
                hashed_password=get_password_hash("password123"),
                is_active=True,
                is_superuser=False
            )
            db.add(regular_user)
        
        # Create authors
        authors = [
            Author(
                name="Leo Tolstoy",
                biography="Russian writer, philosopher",
                nationality="Russia"
            ),
            Author(
                name="Fyodor Dostoevsky", 
                biography="Russian writer, thinker",
                nationality="Russia"
            ),
            Author(
                name="Alexander Pushkin",
                biography="Russian poet, playwright and prose writer",
                nationality="Russia"
            )
        ]
        
        for author in authors:
            db.add(author)
        
        # Create genres
        genres = [
            Genre(name="Classical Literature", description="Works by classical authors"),
            Genre(name="Novel", description="Epic genre"),
            Genre(name="Poetry", description="Poetic works"),
            Genre(name="Drama", description="Dramatic works"),
            Genre(name="Philosophy", description="Philosophical works")
        ]
        
        for genre in genres:
            db.add(genre)
        
        # Save changes to get IDs
        db.commit()
        
        # Create books only in development
        if settings.is_development:
            books_data = [
                {
                    "title": "War and Peace",
                    "description": "Epic novel about Russian society during the Napoleonic Wars",
                    "page_count": 1300,
                    "language": "ru",
                    "price": 599.99,
                    "author_names": ["Leo Tolstoy"],
                    "genre_names": ["Classical Literature", "Novel"]
                },
                {
                    "title": "Crime and Punishment",
                    "description": "Psychological novel about student Raskolnikov",
                    "page_count": 671,
                    "language": "ru", 
                    "price": 449.99,
                    "author_names": ["Fyodor Dostoevsky"],
                    "genre_names": ["Classical Literature", "Novel"]
                },
                {
                    "title": "Eugene Onegin",
                    "description": "Novel in verse about noble society",
                    "page_count": 384,
                    "language": "ru",
                    "price": 299.99,
                    "author_names": ["Alexander Pushkin"],
                    "genre_names": ["Classical Literature", "Poetry"]
                }
            ]
            
            for book_data in books_data:
                book = Book(
                    title=book_data["title"],
                    description=book_data["description"],
                    page_count=book_data["page_count"],
                    language=book_data["language"],
                    price=book_data["price"],
                    is_available=True
                )
                
                # Add authors
                for author_name in book_data["author_names"]:
                    author = db.query(Author).filter(Author.name == author_name).first()
                    if author:
                        book.authors.append(author)
                
                # Add genres
                for genre_name in book_data["genre_names"]:
                    genre = db.query(Genre).filter(Genre.name == genre_name).first()
                    if genre:
                        book.genres.append(genre)
                
                db.add(book)
        
        db.commit()
        print("Test data created successfully!")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()


def get_database_info():
    """Get database information for health check"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        
        # Get migration info
        migration_info = get_migration_info()
        
        return {
            "status": "healthy", 
            "connection": "ok",
            "migrations": migration_info
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}