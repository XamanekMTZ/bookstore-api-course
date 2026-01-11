"""
Конфигурация базы данных с использованием новой системы настроек
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .models import Base
from .config import settings


def create_database_engine():
    """Создание движка базы данных с конфигурацией"""
    db_config = settings.get_database_config()
    
    # Настройки для SQLite
    if db_config["url"].startswith("sqlite"):
        engine = create_engine(
            db_config["url"],
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=db_config["echo"]
        )
    else:
        # Настройки для PostgreSQL и других БД
        engine = create_engine(
            db_config["url"],
            echo=db_config["echo"],
            pool_size=db_config["pool_size"],
            max_overflow=db_config["max_overflow"],
            pool_timeout=db_config["pool_timeout"],
            pool_recycle=db_config["pool_recycle"]
        )
    
    return engine


# Создание движка и сессии
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Создание всех таблиц"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация БД с тестовыми данными"""
    from .models import User, Author, Genre, Book
    from .auth import get_password_hash
    
    create_tables()
    
    # Пропускаем создание тестовых данных в production
    if settings.is_production:
        print("Production environment - skipping test data creation")
        return
    
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже данные
        if db.query(User).first():
            print("База данных уже инициализирована")
            return
        
        print("Создание тестовых данных...")
        
        # Создаем суперпользователя
        admin_user = User(
            email="admin@bookstore.com",
            username="admin",
            full_name="Администратор",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        
        # Создаем обычного пользователя только в development
        if settings.is_development:
            regular_user = User(
                email="user@example.com",
                username="testuser",
                full_name="Тестовый пользователь",
                hashed_password=get_password_hash("password123"),
                is_active=True,
                is_superuser=False
            )
            db.add(regular_user)
        
        # Создаем авторов
        authors = [
            Author(
                name="Лев Толстой",
                biography="Русский писатель, философ",
                nationality="Россия"
            ),
            Author(
                name="Федор Достоевский", 
                biography="Русский писатель, мыслитель",
                nationality="Россия"
            ),
            Author(
                name="Александр Пушкин",
                biography="Русский поэт, драматург и прозаик",
                nationality="Россия"
            )
        ]
        
        for author in authors:
            db.add(author)
        
        # Создаем жанры
        genres = [
            Genre(name="Классическая литература", description="Произведения классиков"),
            Genre(name="Роман", description="Эпический жанр"),
            Genre(name="Поэзия", description="Стихотворные произведения"),
            Genre(name="Драма", description="Драматические произведения"),
            Genre(name="Философия", description="Философские произведения")
        ]
        
        for genre in genres:
            db.add(genre)
        
        # Сохраняем изменения, чтобы получить ID
        db.commit()
        
        # Создаем книги только в development
        if settings.is_development:
            books_data = [
                {
                    "title": "Война и мир",
                    "description": "Роман-эпопея о русском обществе в эпоху наполеоновских войн",
                    "page_count": 1300,
                    "language": "ru",
                    "price": 599.99,
                    "author_names": ["Лев Толстой"],
                    "genre_names": ["Классическая литература", "Роман"]
                },
                {
                    "title": "Преступление и наказание",
                    "description": "Психологический роман о студенте Раскольникове",
                    "page_count": 671,
                    "language": "ru", 
                    "price": 449.99,
                    "author_names": ["Федор Достоевский"],
                    "genre_names": ["Классическая литература", "Роман"]
                },
                {
                    "title": "Евгений Онегин",
                    "description": "Роман в стихах о дворянском обществе",
                    "page_count": 384,
                    "language": "ru",
                    "price": 299.99,
                    "author_names": ["Александр Пушкин"],
                    "genre_names": ["Классическая литература", "Поэзия"]
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
                
                # Добавляем авторов
                for author_name in book_data["author_names"]:
                    author = db.query(Author).filter(Author.name == author_name).first()
                    if author:
                        book.authors.append(author)
                
                # Добавляем жанры
                for genre_name in book_data["genre_names"]:
                    genre = db.query(Genre).filter(Genre.name == genre_name).first()
                    if genre:
                        book.genres.append(genre)
                
                db.add(book)
        
        db.commit()
        print("Тестовые данные созданы успешно!")
        
    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()


def get_database_info():
    """Получение информации о базе данных для health check"""
    try:
        db = SessionLocal()
        result = db.execute("SELECT 1").scalar()
        db.close()
        return {"status": "healthy", "connection": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}