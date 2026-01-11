# 🧪 Тестирование Python - Мастер-класс

## 🎯 Что мы создали

### 📁 Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Конфигурация pytest и фикстуры
├── test_unit_basic.py       # Unit тесты
├── test_api_integration.py  # Интеграционные тесты API
├── test_property_based.py   # Property-based тесты (Hypothesis)
├── test_performance.py      # Тесты производительности
└── factories.py             # Фабрики для тестовых данных
```

### 🔧 Инструменты тестирования

**Основные библиотеки:**
- `pytest` - основной фреймворк тестирования
- `pytest-asyncio` - поддержка асинхронных тестов
- `pytest-cov` - покрытие кода
- `httpx` - HTTP клиент для тестирования API
- `hypothesis` - property-based тестирование
- `factory-boy` - фабрики для создания тестовых данных
- `faker` - генерация фейковых данных

## 🧪 Типы тестов

### 1. Unit тесты
```python
def test_password_hashing():
    """Тест хэширования пароля"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
```

**Что тестируем:**
- Отдельные функции и методы
- Бизнес-логику
- Валидацию данных
- Модели данных

### 2. Интеграционные тесты
```python
def test_create_user(client):
    """Тест создания пользователя через API"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

**Что тестируем:**
- API эндпоинты
- Взаимодействие компонентов
- Аутентификацию и авторизацию
- CRUD операции

### 3. Property-based тесты
```python
@given(password=valid_password())
def test_password_hash_roundtrip(password):
    """Свойство: хэш пароля должен верифицироваться обратно"""
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
```

**Что тестируем:**
- Универсальные свойства
- Инварианты системы
- Граничные случаи
- Математические свойства

### 4. Тесты производительности
```python
def test_search_performance(db_session):
    """Тест производительности поиска"""
    create_test_library(db_session, num_books=200)
    
    start_time = time.perf_counter()
    results = db_session.query(Book).filter(
        Book.title.ilike("%test%")
    ).limit(50).all()
    end_time = time.perf_counter()
    
    assert end_time - start_time < 0.05
```

**Что тестируем:**
- Время выполнения запросов
- Использование памяти
- Параллельные запросы
- Масштабируемость

## 🏭 Фабрики тестовых данных

### Factory Boy
```python
class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
    
    email = factory.LazyAttribute(lambda obj: fake.unique.email())
    username = factory.LazyAttribute(lambda obj: fake.unique.user_name())
    full_name = factory.LazyAttribute(lambda obj: fake.name())
```

**Преимущества:**
- Автоматическая генерация данных
- Связи между объектами
- Различные стратегии создания
- Повторяемость тестов

### Faker для реалистичных данных
```python
fake = Faker(['ru_RU', 'en_US'])

name = fake.name()
email = fake.email()
text = fake.text(max_nb_chars=500)
date = fake.date_between(start_date='-1y', end_date='today')
```

## 🔧 Фикстуры pytest

### Базовые фикстуры
```python
@pytest.fixture
def db_session():
    """Тестовая сессия БД"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Тестовый HTTP клиент"""
    with TestClient(app) as test_client:
        yield test_client
```

### Фикстуры с данными
```python
@pytest.fixture
def test_user(db_session):
    """Создание тестового пользователя"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(user)
    db_session.commit()
    return user
```

## 📊 Покрытие кода

### Конфигурация
```ini
# pytest.ini
[tool:pytest]
addopts = 
    --cov=bookstore
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

### Команды
```bash
# Запуск с покрытием
pytest --cov=bookstore

# HTML отчет
pytest --cov=bookstore --cov-report=html

# Только непокрытые строки
pytest --cov=bookstore --cov-report=term-missing
```

## 🚀 Запуск тестов

### Основные команды
```bash
# Все тесты
pytest

# Конкретный файл
pytest tests/test_unit_basic.py

# Конкретный тест
pytest tests/test_unit_basic.py::TestPasswordHashing::test_password_hashing

# С подробным выводом
pytest -v

# Параллельно
pytest -n auto

# Только быстрые тесты
pytest -m "not slow"
```

### Маркеры
```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_performance():
    pass
```

## 🎯 Лучшие практики

### Структура тестов
- ✅ **AAA паттерн**: Arrange, Act, Assert
- ✅ **Один тест = одна проверка**
- ✅ **Описательные имена тестов**
- ✅ **Изоляция тестов** (каждый тест независим)

### Фикстуры
- ✅ **Минимальные фикстуры** (только необходимые данные)
- ✅ **Правильные scope** (function, class, module, session)
- ✅ **Cleanup** (очистка после тестов)

### Данные
- ✅ **Фабрики вместо хардкода**
- ✅ **Реалистичные данные** (Faker)
- ✅ **Граничные случаи**

### Property-based тесты
- ✅ **Универсальные свойства**
- ✅ **Инварианты системы**
- ✅ **Ограничения на входные данные** (assume)

## 📈 Метрики качества

### Покрытие кода
- **80%+** - хорошее покрытие
- **90%+** - отличное покрытие
- **100%** - не всегда нужно

### Типы покрытия
- **Line coverage** - покрытие строк
- **Branch coverage** - покрытие ветвлений
- **Function coverage** - покрытие функций

### Производительность
- **Unit тесты**: < 1ms каждый
- **Integration тесты**: < 100ms каждый
- **E2E тесты**: < 1s каждый

## 🔍 Отладка тестов

### Полезные опции
```bash
# Остановка на первой ошибке
pytest -x

# Подробный traceback
pytest --tb=long

# Показать print statements
pytest -s

# Запуск конкретного теста в отладчике
pytest --pdb tests/test_unit_basic.py::test_function
```

### Логирование в тестах
```python
import logging

def test_with_logging(caplog):
    with caplog.at_level(logging.INFO):
        function_that_logs()
    
    assert "Expected message" in caplog.text
```

## 🎉 Результат

**За 4 часа мы создали:**
- ✅ Комплексную систему тестирования
- ✅ Unit, интеграционные, property-based тесты
- ✅ Фабрики для тестовых данных
- ✅ Тесты производительности
- ✅ Конфигурацию pytest с покрытием
- ✅ Makefile для автоматизации

**Теперь ты знаешь как:**
- Писать качественные тесты
- Использовать современные инструменты
- Измерять покрытие кода
- Тестировать производительность
- Автоматизировать тестирование

**Следующий шаг: DevOps + Docker + CI/CD!** 🚀