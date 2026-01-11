#!/usr/bin/env python3
"""
Создание тестовых данных через API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_data():
    """Создание тестовых данных через API"""
    print("🔧 Создание тестовых данных через API...")
    
    # 1. Создаем обычного пользователя
    print("👤 Создание пользователя...")
    user_data = {
        "email": "user@example.com",
        "username": "testuser",
        "full_name": "Тестовый пользователь",
        "password": "password123",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/users/", json=user_data)
    if response.status_code == 201:
        print("✅ Пользователь создан")
        user = response.json()
    else:
        print(f"❌ Ошибка создания пользователя: {response.status_code}")
        print(response.text)
        return
    
    # 2. Входим в систему
    print("🔐 Вход в систему...")
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Успешный вход")
    else:
        print(f"❌ Ошибка входа: {response.status_code}")
        print(response.text)
        return
    
    # Проверяем, есть ли уже данные
    response = requests.get(f"{BASE_URL}/api/v1/books/")
    if response.status_code == 200 and len(response.json()) > 0:
        print("📚 Книги уже существуют")
        return
    
    print("📚 Данные будут созданы администратором...")
    print("Для создания книг нужны права суперпользователя")
    print("Используйте админ-панель или создайте суперпользователя")

if __name__ == "__main__":
    try:
        create_test_data()
    except requests.exceptions.ConnectionError:
        print("❌ API недоступен. Запустите сервер командой: python run_bookstore.py")