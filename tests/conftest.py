"""
Конфигурация pytest и фикстуры
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from bookstore.main import app
from bookstore.database import get_db, Base
from bookstore.models import User, Author, Genre, Book
from bookstore.auth import get_password_hash, create_access_token

# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Переопределение зависимости БД для тестов"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Переопределяем зависимость
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для всей сессии тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Создание тестовой сессии БД для каждого теста"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Тестовый клиент FastAPI"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный тестовый клиент"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user(db_session) -> User:
    """Создание тестового пользователя"""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_superuser(db_session) -> User:
    """Создание тестового суперпользователя"""
    user = User(
        email="admin@example.com",
        username="admin",
        full_name="Admin User",
        hashed_password=get_password_hash("adminpass123"),
        is_active=True,
        is_superuser=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user) -> str:
    """JWT токен для обычного пользователя"""
    return create_access_token(data={"sub": test_user.username})


@pytest.fixture
def admin_token(test_superuser) -> str:
    """JWT токен для суперпользователя"""
    return create_access_token(data={"sub": test_superuser.username})


@pytest.fixture
def auth_headers(user_token) -> dict:
    """Заголовки авторизации для обычного пользователя"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token) -> dict:
    """Заголовки авторизации для админа"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def test_author(db_session) -> Author:
    """Создание тестового автора"""
    author = Author(
        name="Test Author",
        biography="Test biography",
        nationality="Test Country"
    )
    db_session.add(author)
    db_session.commit()
    db_session.refresh(author)
    return author


@pytest.fixture
def test_genre(db_session) -> Genre:
    """Создание тестового жанра"""
    genre = Genre(
        name="Test Genre",
        description="Test genre description"
    )
    db_session.add(genre)
    db_session.commit()
    db_session.refresh(genre)
    return genre


@pytest.fixture
def test_book(db_session, test_author, test_genre) -> Book:
    """Создание тестовой книги"""
    book = Book(
        title="Test Book",
        description="Test book description",
        price=99.99,
        page_count=200,
        language="en",
        is_available=True
    )
    book.authors = [test_author]
    book.genres = [test_genre]
    
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book