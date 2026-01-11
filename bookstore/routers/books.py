"""
Роутер для работы с книгами
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from ..database import get_db
from ..models import Book, Author, Genre, Review
from ..schemas import (
    Book as BookSchema, BookCreate, BookUpdate, BookWithStats,
    BookSearchParams, BookSortBy, SortOrder, PaginatedResponse
)
from ..auth import get_current_active_user, get_current_superuser
from ..models import User

router = APIRouter()


def get_books_query(
    db: Session,
    search_params: Optional[BookSearchParams] = None,
    sort_by: BookSortBy = BookSortBy.CREATED_AT,
    sort_order: SortOrder = SortOrder.DESC
):
    """Базовый запрос для получения книг с фильтрацией и сортировкой"""
    query = db.query(Book).options(
        joinedload(Book.authors),
        joinedload(Book.genres)
    )
    
    if search_params:
        # Поиск по названию и описанию
        if search_params.q:
            search_term = f"%{search_params.q}%"
            query = query.filter(
                or_(
                    Book.title.ilike(search_term),
                    Book.description.ilike(search_term)
                )
            )
        
        # Фильтр по автору
        if search_params.author:
            query = query.join(Book.authors).filter(
                Author.name.ilike(f"%{search_params.author}%")
            )
        
        # Фильтр по жанру
        if search_params.genre:
            query = query.join(Book.genres).filter(
                Genre.name.ilike(f"%{search_params.genre}%")
            )
        
        # Фильтр по цене
        if search_params.min_price is not None:
            query = query.filter(Book.price >= search_params.min_price)
        
        if search_params.max_price is not None:
            query = query.filter(Book.price <= search_params.max_price)
        
        # Фильтр по языку
        if search_params.language:
            query = query.filter(Book.language == search_params.language)
        
        # Только доступные книги
        if search_params.available_only:
            query = query.filter(Book.is_available == True)
    
    # Сортировка
    if sort_by == BookSortBy.TITLE:
        order_field = Book.title
    elif sort_by == BookSortBy.PRICE:
        order_field = Book.price
    elif sort_by == BookSortBy.PUBLICATION_DATE:
        order_field = Book.publication_date
    elif sort_by == BookSortBy.RATING:
        # Сортировка по рейтингу требует подзапроса
        avg_rating = db.query(func.avg(Review.rating)).filter(Review.book_id == Book.id).scalar_subquery()
        order_field = avg_rating
    else:
        order_field = Book.created_at
    
    if sort_order == SortOrder.DESC:
        query = query.order_by(order_field.desc())
    else:
        query = query.order_by(order_field.asc())
    
    return query


@router.get("/", response_model=List[BookSchema])
async def get_books(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Поисковый запрос"),
    author: Optional[str] = Query(None, description="Имя автора"),
    genre: Optional[str] = Query(None, description="Жанр"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    language: Optional[str] = Query(None, description="Язык"),
    available_only: bool = Query(True, description="Только доступные книги"),
    sort_by: BookSortBy = Query(BookSortBy.CREATED_AT, description="Поле для сортировки"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="Порядок сортировки"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы")
):
    """Получение списка книг с поиском и фильтрацией"""
    search_params = BookSearchParams(
        q=q, author=author, genre=genre,
        min_price=min_price, max_price=max_price,
        language=language, available_only=available_only
    )
    
    query = get_books_query(db, search_params, sort_by, sort_order)
    
    # Пагинация
    offset = (page - 1) * size
    books = query.offset(offset).limit(size).all()
    
    return books


@router.get("/stats")
async def get_books_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получение статистики по книгам"""
    total_books = db.query(Book).count()
    available_books = db.query(Book).filter(Book.is_available == True).count()
    total_authors = db.query(Author).count()
    total_genres = db.query(Genre).count()
    
    # Средняя цена
    avg_price = db.query(func.avg(Book.price)).filter(Book.price.isnot(None)).scalar()
    
    return {
        "total_books": total_books,
        "available_books": available_books,
        "total_authors": total_authors,
        "total_genres": total_genres,
        "average_price": round(avg_price, 2) if avg_price else None
    }


@router.get("/{book_id}", response_model=BookWithStats)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """Получение книги по ID"""
    book = db.query(Book).options(
        joinedload(Book.authors),
        joinedload(Book.genres),
        joinedload(Book.reviews)
    ).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Вычисляем статистику
    reviews = book.reviews
    review_count = len(reviews)
    average_rating = sum(review.rating for review in reviews) / review_count if review_count > 0 else None
    
    # Создаем объект с дополнительными полями
    book_dict = {
        **book.__dict__,
        "authors": book.authors,
        "genres": book.genres,
        "average_rating": average_rating,
        "review_count": review_count
    }
    
    return BookWithStats(**book_dict)


@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Создание новой книги (только для суперпользователей)"""
    
    # Проверяем существование авторов
    authors = db.query(Author).filter(Author.id.in_(book_data.author_ids)).all()
    if len(authors) != len(book_data.author_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more authors not found"
        )
    
    # Проверяем существование жанров
    genres = db.query(Genre).filter(Genre.id.in_(book_data.genre_ids)).all()
    if len(genres) != len(book_data.genre_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more genres not found"
        )
    
    # Проверяем уникальность ISBN
    if book_data.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book_data.isbn).first()
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this ISBN already exists"
            )
    
    # Создаем книгу
    book_dict = book_data.model_dump(exclude={"author_ids", "genre_ids"})
    book = Book(**book_dict)
    
    # Добавляем авторов и жанры
    book.authors = authors
    book.genres = genres
    
    db.add(book)
    db.commit()
    db.refresh(book)
    
    return book


@router.put("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Обновление книги (только для суперпользователей)"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Обновляем поля
    update_data = book_data.model_dump(exclude_unset=True, exclude={"author_ids", "genre_ids"})
    
    for field, value in update_data.items():
        setattr(book, field, value)
    
    # Обновляем авторов, если указаны
    if book_data.author_ids is not None:
        authors = db.query(Author).filter(Author.id.in_(book_data.author_ids)).all()
        if len(authors) != len(book_data.author_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more authors not found"
            )
        book.authors = authors
    
    # Обновляем жанры, если указаны
    if book_data.genre_ids is not None:
        genres = db.query(Genre).filter(Genre.id.in_(book_data.genre_ids)).all()
        if len(genres) != len(book_data.genre_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more genres not found"
            )
        book.genres = genres
    
    db.commit()
    db.refresh(book)
    
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Удаление книги (только для суперпользователей)"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    db.delete(book)
    db.commit()
    
    return None