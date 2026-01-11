#!/usr/bin/env python3
"""
Создание тестовых данных для BookStore API
"""

from bookstore.database import SessionLocal
from bookstore.models import User, Author, Genre, Book
from bookstore.auth import get_password_hash

def create_test_data():
    """Создание тестовых данных"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже данные
        if db.query(User).first():
            print("Данные уже существуют")
            return
        
        print("Создание тестовых данных...")
        
        # Создаем пользователей
        admin_user = User(
            email="admin@bookstore.com",
            username="admin",
            full_name="Администратор",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        
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
            Author(name="Лев Толстой", biography="Русский писатель", nationality="Россия"),
            Author(name="Федор Достоевский", biography="Русский писатель", nationality="Россия"),
            Author(name="Александр Пушкин", biography="Русский поэт", nationality="Россия")
        ]
        
        for author in authors:
            db.add(author)
        
        # Создаем жанры
        genres = [
            Genre(name="Классическая литература", description="Произведения классиков"),
            Genre(name="Роман", description="Эпический жанр"),
            Genre(name="Поэзия", description="Стихотворные произведения")
        ]
        
        for genre in genres:
            db.add(genre)
        
        # Сохраняем, чтобы получить ID
        db.commit()
        
        # Создаем книги
        book1 = Book(
            title="Война и мир",
            description="Роман-эпопея о русском обществе",
            page_count=1300,
            language="ru",
            price=599.99,
            is_available=True
        )
        book1.authors = [authors[0]]  # Лев Толстой
        book1.genres = [genres[0], genres[1]]  # Классика, Роман
        db.add(book1)
        
        book2 = Book(
            title="Преступление и наказание",
            description="Психологический роман",
            page_count=671,
            language="ru",
            price=449.99,
            is_available=True
        )
        book2.authors = [authors[1]]  # Достоевский
        book2.genres = [genres[0], genres[1]]  # Классика, Роман
        db.add(book2)
        
        book3 = Book(
            title="Евгений Онегин",
            description="Роман в стихах",
            page_count=384,
            language="ru",
            price=299.99,
            is_available=True
        )
        book3.authors = [authors[2]]  # Пушкин
        book3.genres = [genres[0], genres[2]]  # Классика, Поэзия
        db.add(book3)
        
        db.commit()
        print("✅ Тестовые данные созданы успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()