"""
Pydantic схемы для валидации данных
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Union
from datetime import datetime
from enum import Enum


# Базовые схемы
class TimestampMixin(BaseModel):
    """Миксин для временных меток"""
    created_at: datetime
    updated_at: Optional[datetime] = None


# Пользователи
class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class UserInDB(UserBase, TimestampMixin):
    """Схема пользователя в БД"""
    class Config:
        from_attributes = True
    
    id: int
    is_superuser: bool = False


class User(UserInDB):
    """Публичная схема пользователя"""
    pass


# Авторы
class AuthorBase(BaseModel):
    """Базовая схема автора"""
    name: str = Field(..., min_length=1, max_length=255)
    biography: Optional[str] = None
    birth_date: Optional[datetime] = None
    death_date: Optional[datetime] = None
    nationality: Optional[str] = Field(None, max_length=100)


class AuthorCreate(AuthorBase):
    """Схема для создания автора"""
    pass


class AuthorUpdate(BaseModel):
    """Схема для обновления автора"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    biography: Optional[str] = None
    birth_date: Optional[datetime] = None
    death_date: Optional[datetime] = None
    nationality: Optional[str] = Field(None, max_length=100)


class Author(AuthorBase, TimestampMixin):
    """Схема автора"""
    class Config:
        from_attributes = True
    
    id: int


# Жанры
class GenreBase(BaseModel):
    """Базовая схема жанра"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class GenreCreate(GenreBase):
    """Схема для создания жанра"""
    pass


class GenreUpdate(BaseModel):
    """Схема для обновления жанра"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class Genre(GenreBase):
    """Схема жанра"""
    class Config:
        from_attributes = True
    
    id: int
    created_at: datetime


# Книги
class BookBase(BaseModel):
    """Базовая схема книги"""
    title: str = Field(..., min_length=1, max_length=500)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    publication_date: Optional[datetime] = None
    page_count: Optional[int] = Field(None, gt=0)
    language: str = Field(default="ru", max_length=10)
    price: Optional[float] = Field(None, ge=0)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    is_available: bool = True


class BookCreate(BookBase):
    """Схема для создания книги"""
    author_ids: List[int] = Field(..., min_items=1)
    genre_ids: List[int] = Field(..., min_items=1)


class BookUpdate(BaseModel):
    """Схема для обновления книги"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    isbn: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    publication_date: Optional[datetime] = None
    page_count: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, max_length=10)
    price: Optional[float] = Field(None, ge=0)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None
    author_ids: Optional[List[int]] = None
    genre_ids: Optional[List[int]] = None


class Book(BookBase, TimestampMixin):
    """Схема книги"""
    class Config:
        from_attributes = True
    
    id: int
    authors: List[Author] = []
    genres: List[Genre] = []


class BookWithStats(Book):
    """Книга со статистикой"""
    average_rating: Optional[float] = None
    review_count: int = 0


# Отзывы
class ReviewBase(BaseModel):
    """Базовая схема отзыва"""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Схема для создания отзыва"""
    book_id: int


class ReviewUpdate(BaseModel):
    """Схема для обновления отзыва"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None


class Review(ReviewBase, TimestampMixin):
    """Схема отзыва"""
    class Config:
        from_attributes = True
    
    id: int
    user_id: int
    book_id: int
    user: User
    book: Book


# Списки для чтения
class ReadingListBase(BaseModel):
    """Базовая схема списка для чтения"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False


class ReadingListCreate(ReadingListBase):
    """Схема для создания списка"""
    pass


class ReadingListUpdate(BaseModel):
    """Схема для обновления списка"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None


class ReadingListItemBase(BaseModel):
    """Базовая схема элемента списка"""
    book_id: int
    notes: Optional[str] = None


class ReadingListItemCreate(ReadingListItemBase):
    """Схема для добавления книги в список"""
    pass


class ReadingListItem(ReadingListItemBase):
    """Схема элемента списка"""
    class Config:
        from_attributes = True
    
    id: int
    reading_list_id: int
    added_at: datetime
    book: Book


class ReadingList(ReadingListBase, TimestampMixin):
    """Схема списка для чтения"""
    class Config:
        from_attributes = True
    
    id: int
    user_id: int
    user: User
    items: List[ReadingListItem] = []


# Аутентификация
class Token(BaseModel):
    """Схема токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные токена"""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Запрос на вход"""
    username: str
    password: str


# Поиск и фильтрация
class BookSearchParams(BaseModel):
    """Параметры поиска книг"""
    q: Optional[str] = Field(None, description="Поисковый запрос")
    author: Optional[str] = Field(None, description="Имя автора")
    genre: Optional[str] = Field(None, description="Жанр")
    min_price: Optional[float] = Field(None, ge=0, description="Минимальная цена")
    max_price: Optional[float] = Field(None, ge=0, description="Максимальная цена")
    language: Optional[str] = Field(None, description="Язык")
    available_only: bool = Field(True, description="Только доступные книги")


class SortOrder(str, Enum):
    """Порядок сортировки"""
    ASC = "asc"
    DESC = "desc"


class BookSortBy(str, Enum):
    """Поля для сортировки книг"""
    TITLE = "title"
    PRICE = "price"
    PUBLICATION_DATE = "publication_date"
    CREATED_AT = "created_at"
    RATING = "rating"


# Пагинация
class PaginationParams(BaseModel):
    """Параметры пагинации"""
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Размер страницы")


class PaginatedResponse(BaseModel):
    """Ответ с пагинацией"""
    items: List[Union[Book, Author, Genre, Review, ReadingList]]
    total: int
    page: int
    size: int
    pages: int


# Статистика
class BookStats(BaseModel):
    """Статистика книги"""
    total_books: int
    available_books: int
    total_authors: int
    total_genres: int
    average_price: Optional[float]


class UserStats(BaseModel):
    """Статистика пользователя"""
    total_users: int
    active_users: int
    total_reviews: int
    total_reading_lists: int