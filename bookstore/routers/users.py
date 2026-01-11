"""
Роутер для работы с пользователями
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User as UserModel
from ..schemas import User, UserCreate, UserUpdate
from ..auth import (
    get_current_active_user, get_current_superuser,
    get_password_hash, get_user_by_email, get_user_by_username,
    check_user_permissions
)

router = APIRouter()


@router.get("/", response_model=List[User])
async def get_users(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """Получение списка пользователей (только для суперпользователей)"""
    users = db.query(UserModel).all()
    return users


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_active_user)
):
    """Получение информации о текущем пользователе"""
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Получение пользователя по ID"""
    if not check_user_permissions(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    
    # Проверяем уникальность email
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Проверяем уникальность username
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Создаем пользователя
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["hashed_password"] = get_password_hash(user_data.password)
    
    user = UserModel(**user_dict)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Обновление пользователя"""
    if not check_user_permissions(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Проверяем уникальность email, если он изменяется
    if "email" in update_data and update_data["email"] != user.email:
        if get_user_by_email(db, update_data["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Проверяем уникальность username, если он изменяется
    if "username" in update_data and update_data["username"] != user.username:
        if get_user_by_username(db, update_data["username"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """Удаление пользователя (только для суперпользователей)"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    return None