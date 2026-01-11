"""
Фабрики для создания тестовых данных
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from datetime import datetime, timedelta
import random

from bookstore.models import User, Author, Genre, Book, Review, ReadingList
from bookstore.auth import get_password_hash

fake = Faker(['ru_RU', 'en_US'])


class UserFactory(SQLAlchemyModelFactory):
    """Фабрика для создания пользователей"""
    
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
    
    email = factory.LazyAttribute(lambda obj: fake.unique.email())
    username = factory.LazyAttribute(lambda obj: fake.unique.user_name())
    full_name = factory.LazyAttribute(lambda obj: fake.name())
    hashed_password = factory.LazyAttribute(lambda obj: get_password_hash("testpass123"))
    is_active = True
    is_superuser = False


class SuperUserFactory(UserFactory):
    """Фабрика для создания суперпользователей"""
    is_superuser = True
    username = factory.Sequence(lambda n: f"admin{n}")
    email = factory.Sequence(lambda n: f"admin{n}@example.com")


class AuthorFactory(SQLAlchemyModelFactory):
    """Фабрика для создания авторов"""
    
    class Meta:
        model = Author
        sqlalchemy_session_persistence = "commit"
    
    name = factory.LazyAttribute(lambda obj: fake.name())
    biography = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=500))
    nationality = factory.LazyAttribute(lambda obj: fake.country())
    birth_date = factory.LazyAttribute(
        lambda obj: fake.date_between(start_date='-100y', end_date='-20y')
    )
    death_date = factory.LazyAttribute(
        lambda obj: fake.date_between(start_date='-20y', end_date='today') 
        if random.choice([True, False]) else None
    )


class GenreFactory(SQLAlchemyModelFactory):
    """Фабрика для создания жанров"""
    
    class Meta:
        model = Genre
        sqlalchemy_session_persistence = "commit"
    
    name = factory.LazyAttribute(lambda obj: fake.unique.word().title())
    description = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=200))


class BookFactory(SQLAlchemyModelFactory):
    """Фабрика для создания книг"""
    
    class Meta:
        model = Book
        sqlalchemy_session_persistence = "commit"
    
    title = factory.LazyAttribute(lambda obj: fake.sentence(nb_words=4).rstrip('.'))
    description = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=1000))
    isbn = factory.LazyAttribute(lambda obj: fake.isbn13())
    publication_date = factory.LazyAttribute(
        lambda obj: fake.date_between(start_date='-50y', end_date='today')
    )
    page_count = factory.LazyAttribute(lambda obj: fake.random_int(min=50, max=1500))
    language = factory.LazyAttribute(lambda obj: fake.random_element(['ru', 'en', 'fr', 'de']))
    price = factory.LazyAttribute(lambda obj: round(fake.pyfloat(min_value=9.99, max_value=999.99, right_digits=2), 2))
    cover_image_url = factory.LazyAttribute(lambda obj: fake.image_url())
    is_available = factory.LazyAttribute(lambda obj: fake.boolean(chance_of_getting_true=90))
    
    # Связи many-to-many
    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for author in extracted:
                self.authors.append(author)
        else:
            # Создаем 1-3 авторов по умолчанию
            author_count = fake.random_int(min=1, max=3)
            for _ in range(author_count):
                author = AuthorFactory()
                self.authors.append(author)
    
    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for genre in extracted:
                self.genres.append(genre)
        else:
            # Создаем 1-2 жанра по умолчанию
            genre_count = fake.random_int(min=1, max=2)
            for _ in range(genre_count):
                genre = GenreFactory()
                self.genres.append(genre)


class ReviewFactory(SQLAlchemyModelFactory):
    """Фабрика для создания отзывов"""
    
    class Meta:
        model = Review
        sqlalchemy_session_persistence = "commit"
    
    user = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)
    rating = factory.LazyAttribute(lambda obj: fake.random_int(min=1, max=5))
    title = factory.LazyAttribute(lambda obj: fake.sentence(nb_words=6).rstrip('.'))
    content = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=500))


class ReadingListFactory(SQLAlchemyModelFactory):
    """Фабрика для создания списков чтения"""
    
    class Meta:
        model = ReadingList
        sqlalchemy_session_persistence = "commit"
    
    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda obj: fake.sentence(nb_words=3).rstrip('.'))
    description = factory.LazyAttribute(lambda obj: fake.text(max_nb_chars=300))
    is_public = factory.LazyAttribute(lambda obj: fake.boolean(chance_of_getting_true=30))


# Специальные фабрики для тестовых сценариев

class PopularBookFactory(BookFactory):
    """Фабрика для популярных книг"""
    price = factory.LazyAttribute(lambda obj: round(fake.pyfloat(min_value=299.99, max_value=799.99, right_digits=2), 2))
    page_count = factory.LazyAttribute(lambda obj: fake.random_int(min=300, max=800))
    is_available = True


class ClassicBookFactory(BookFactory):
    """Фабрика для классических книг"""
    publication_date = factory.LazyAttribute(
        lambda obj: fake.date_between(start_date='-200y', end_date='-50y')
    )
    page_count = factory.LazyAttribute(lambda obj: fake.random_int(min=200, max=1000))
    language = 'ru'


class NewBookFactory(BookFactory):
    """Фабрика для новых книг"""
    publication_date = factory.LazyAttribute(
        lambda obj: fake.date_between(start_date='-2y', end_date='today')
    )
    is_available = True


class ExpensiveBookFactory(BookFactory):
    """Фабрика для дорогих книг"""
    price = factory.LazyAttribute(lambda obj: round(fake.pyfloat(min_value=500.0, max_value=2000.0, right_digits=2), 2))


class FreeBookFactory(BookFactory):
    """Фабрика для бесплатных книг"""
    price = 0.0


# Batch фабрики для создания множества объектов

def create_test_library(db_session, num_books=50):
    """Создание тестовой библиотеки"""
    # Настраиваем все фабрики для работы с переданной сессией
    UserFactory._meta.sqlalchemy_session = db_session
    SuperUserFactory._meta.sqlalchemy_session = db_session
    AuthorFactory._meta.sqlalchemy_session = db_session
    GenreFactory._meta.sqlalchemy_session = db_session
    BookFactory._meta.sqlalchemy_session = db_session
    ReviewFactory._meta.sqlalchemy_session = db_session
    ReadingListFactory._meta.sqlalchemy_session = db_session
    
    # Создаем пользователей
    users = UserFactory.create_batch(10)
    admin = SuperUserFactory()
    
    # Создаем авторов и жанры
    authors = AuthorFactory.create_batch(20)
    genres = GenreFactory.create_batch(10)
    
    # Создаем книги
    books = []
    for _ in range(num_books):
        book_authors = fake.random_elements(authors, length=fake.random_int(1, 3), unique=True)
        book_genres = fake.random_elements(genres, length=fake.random_int(1, 2), unique=True)
        
        book = BookFactory(authors=book_authors, genres=book_genres)
        books.append(book)
    
    # Создаем отзывы
    for _ in range(min(num_books * 2, 100)):  # Ограничиваем количество отзывов
        user = fake.random_element(users)
        book = fake.random_element(books)
        
        # Проверяем, что пользователь еще не оставлял отзыв на эту книгу
        existing_review = db_session.query(Review).filter(
            Review.user_id == user.id,
            Review.book_id == book.id
        ).first()
        
        if not existing_review:
            ReviewFactory(user=user, book=book)
    
    # Создаем списки чтения (упрощенно)
    for user in users[:5]:  # Только для первых 5 пользователей
        if fake.boolean(chance_of_getting_true=70):  # 70% пользователей имеют списки
            reading_list = ReadingListFactory(user=user)
            
            # Добавляем книги в список
            list_books = fake.random_elements(books, length=fake.random_int(3, 10), unique=True)
            for book in list_books:
                from bookstore.models import ReadingListItem
                item = ReadingListItem(
                    reading_list_id=reading_list.id,
                    book_id=book.id,
                    notes=fake.sentence() if fake.boolean() else None
                )
                db_session.add(item)
    
    db_session.commit()
    
    return {
        'users': users,
        'admin': admin,
        'authors': authors,
        'genres': genres,
        'books': books
    }