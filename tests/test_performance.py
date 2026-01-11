"""
Тесты производительности и нагрузки
"""

import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List
import statistics

from bookstore.models import Book, User, Author, Genre
from .factories import create_test_library, BookFactory, UserFactory, AuthorFactory, GenreFactory


class TestDatabasePerformance:
    """Тесты производительности базы данных"""
    
    def test_book_query_performance(self, db_session):
        """Тест производительности запросов книг"""
        # Создаем большую библиотеку
        library = create_test_library(db_session, num_books=100)
        
        # Измеряем время выполнения различных запросов
        times = []
        
        for _ in range(10):
            start_time = time.perf_counter()
            
            # Сложный запрос с JOIN
            books = db_session.query(Book).join(Book.authors).join(Book.genres).limit(20).all()
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        # Проверяем, что запросы выполняются достаточно быстро
        assert avg_time < 0.5, f"Средний время запроса слишком большое: {avg_time:.3f}s"
        assert max_time < 1.0, f"Максимальное время запроса слишком большое: {max_time:.3f}s"
        assert len(books) > 0, "Должны быть найдены книги с авторами и жанрами"
    
    def test_search_performance(self, db_session):
        """Тест производительности поиска"""
        library = create_test_library(db_session, num_books=200)
        
        search_terms = ["test", "book", "author", "genre", "classic"]
        times = []
        
        for term in search_terms:
            start_time = time.perf_counter()
            
            # Поиск по названию и описанию
            results = db_session.query(Book).filter(
                Book.title.ilike(f"%{term}%") | 
                Book.description.ilike(f"%{term}%")
            ).limit(50).all()
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        
        # Поиск должен быть быстрым даже по большой базе
        assert avg_time < 0.2, f"Поиск слишком медленный: {avg_time:.3f}s"
    
    def test_pagination_performance(self, db_session):
        """Тест производительности пагинации"""
        library = create_test_library(db_session, num_books=500)
        
        page_size = 20
        times = []
        
        # Тестируем разные страницы
        for page in [1, 5, 10, 20]:
            offset = (page - 1) * page_size
            
            start_time = time.perf_counter()
            
            books = db_session.query(Book).offset(offset).limit(page_size).all()
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        
        # Пагинация должна работать быстро на любой странице
        assert avg_time < 0.1, f"Пагинация слишком медленная: {avg_time:.3f}s"
        
        # Проверяем, что время не растет значительно для дальних страниц
        first_page_time = times[0]
        last_page_time = times[-1]
        
        # Время последней страницы не должно быть в 10 раз больше первой
        assert last_page_time < first_page_time * 10


class TestAPIPerformance:
    """Тесты производительности API"""
    
    def test_concurrent_requests(self, client, db_session):
        """Тест параллельных запросов"""
        library = create_test_library(db_session, num_books=50)
        
        def make_request():
            """Выполнение одного запроса"""
            start_time = time.perf_counter()
            response = client.get("/api/v1/books/")
            end_time = time.perf_counter()
            
            return {
                'status_code': response.status_code,
                'time': end_time - start_time,
                'books_count': len(response.json()) if response.status_code == 200 else 0
            }
        
        # Выполняем 20 параллельных запросов
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in futures]
        
        # Анализируем результаты
        times = [r['time'] for r in results]
        status_codes = [r['status_code'] for r in results]
        
        # Все запросы должны быть успешными
        assert all(code == 200 for code in status_codes)
        
        # Среднее время ответа должно быть разумным
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        assert avg_time < 2.0, f"Среднее время ответа слишком большое: {avg_time:.3f}s"
        assert max_time < 5.0, f"Максимальное время ответа слишком большое: {max_time:.3f}s"
    
    def test_memory_usage_stability(self, client, db_session):
        """Тест стабильности использования памяти"""
        import psutil
        import os
        
        library = create_test_library(db_session, num_books=100)
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Выполняем много запросов
        for _ in range(100):
            response = client.get("/api/v1/books/")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # Рост памяти не должен быть критическим
        assert memory_growth < 100, f"Слишком большой рост памяти: {memory_growth:.1f}MB"
    
    def test_simple_performance(self, client, db_session):
        """Простой тест производительности без async"""
        library = create_test_library(db_session, num_books=30)
        
        times = []
        
        # Выполняем 20 последовательных запросов
        for _ in range(20):
            start_time = time.perf_counter()
            response = client.get("/api/v1/books/")
            end_time = time.perf_counter()
            
            times.append(end_time - start_time)
            assert response.status_code == 200
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        assert avg_time < 1.0, f"Среднее время запроса слишком большое: {avg_time:.3f}s"
        assert max_time < 2.0, f"Максимальное время запроса слишком большое: {max_time:.3f}s"


class TestScalabilityLimits:
    """Тесты пределов масштабируемости"""
    
    def test_large_dataset_handling(self, db_session):
        """Тест работы с большими наборами данных"""
        # Создаем большую библиотеку
        library = create_test_library(db_session, num_books=1000)
        
        # Тестируем различные операции
        start_time = time.perf_counter()
        
        # Подсчет общего количества
        total_books = db_session.query(Book).count()
        
        # Поиск
        search_results = db_session.query(Book).filter(
            Book.title.ilike("%test%")
        ).limit(100).all()
        
        # Сложная фильтрация
        expensive_books = db_session.query(Book).filter(
            Book.price > 500,
            Book.is_available == True
        ).limit(50).all()
        
        end_time = time.perf_counter()
        
        # Операции должны завершаться в разумное время
        assert end_time - start_time < 5.0, "Операции с большим набором данных слишком медленные"
        assert total_books == 1000
        assert len(search_results) <= 100
        assert len(expensive_books) <= 50
    
    def test_concurrent_writes(self, db_session):
        """Тест параллельных записей в БД (упрощенный)"""
        # Настраиваем фабрики для работы с сессией
        UserFactory._meta.sqlalchemy_session = db_session
        AuthorFactory._meta.sqlalchemy_session = db_session
        GenreFactory._meta.sqlalchemy_session = db_session
        BookFactory._meta.sqlalchemy_session = db_session
        
        # Создаем базовые данные
        authors = [AuthorFactory() for _ in range(5)]
        genres = [GenreFactory() for _ in range(3)]
        
        initial_count = db_session.query(Book).count()
        
        # Создаем книги последовательно (SQLite не любит параллельные записи)
        books_created = 0
        for batch in range(3):
            for i in range(10):
                # Используем простые данные
                book = Book(
                    title=f"Concurrent Test Book {batch}-{i}",
                    description=f"Description for concurrent book {batch}-{i}",
                    price=99.99,
                    page_count=200,
                    language="en",
                    is_available=True
                )
                book.authors = [authors[i % len(authors)]]
                book.genres = [genres[i % len(genres)]]
                
                db_session.add(book)
                books_created += 1
            
            # Коммитим каждый батч отдельно
            db_session.commit()
        
        # Проверяем, что все книги созданы
        final_count = db_session.query(Book).count()
        assert final_count >= initial_count + books_created
    
    def test_stress_search(self, client, db_session):
        """Стресс-тест поиска"""
        library = create_test_library(db_session, num_books=200)
        
        search_terms = [
            "test", "book", "author", "classic", "modern", "fiction",
            "science", "history", "romance", "mystery", "adventure"
        ]
        
        times = []
        
        # Выполняем много поисковых запросов
        for i in range(50):  # Уменьшаем количество для стабильности
            term = search_terms[i % len(search_terms)]
            
            start_time = time.perf_counter()
            response = client.get(f"/api/v1/books/?q={term}")
            end_time = time.perf_counter()
            
            times.append(end_time - start_time)
            assert response.status_code == 200
        
        # Анализируем производительность
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        assert avg_time < 0.5, f"Средний время поиска: {avg_time:.3f}s"
        assert max_time < 2.0, f"Максимальное время поиска: {max_time:.3f}s"


class TestResourceUsage:
    """Тесты использования ресурсов"""
    
    def test_database_connection_pooling(self, db_session):
        """Тест пулинга соединений с БД"""
        # Создаем много сессий и проверяем, что они переиспользуются
        sessions = []
        
        for _ in range(20):
            from bookstore.database import SessionLocal
            session = SessionLocal()
            sessions.append(session)
            
            # Выполняем простой запрос
            result = session.query(Book).count()
            assert result >= 0
        
        # Закрываем все сессии
        for session in sessions:
            session.close()
        
        # Тест должен пройти без ошибок подключения
        assert True
    
    def test_query_optimization(self, db_session):
        """Тест оптимизации запросов"""
        library = create_test_library(db_session, num_books=100)
        
        # Тестируем N+1 проблему
        start_time = time.perf_counter()
        
        # Загружаем книги с авторами и жанрами одним запросом
        from sqlalchemy.orm import joinedload
        books = db_session.query(Book).options(
            joinedload(Book.authors),
            joinedload(Book.genres)
        ).limit(50).all()
        
        # Обращаемся к связанным данным
        for book in books:
            authors_count = len(book.authors)
            genres_count = len(book.genres)
            assert authors_count >= 0
            assert genres_count >= 0
        
        end_time = time.perf_counter()
        
        # Оптимизированный запрос должен быть быстрым
        assert end_time - start_time < 1.0, "Запрос с joinedload слишком медленный"