# 🎭 Декораторы + Type Hints - Шпаргалка

## 🎯 Что мы изучили (10:30-12:00)

### 1. Собственные декораторы

#### Базовый шаблон
```python
import functools
from typing import TypeVar, Callable, Any

F = TypeVar('F', bound=Callable[..., Any])

def my_decorator(func: F) -> F:
    @functools.wraps(func)  # Сохраняет метаданные функции
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Логика до выполнения
        result = func(*args, **kwargs)
        # Логика после выполнения
        return result
    return wrapper  # type: ignore
```

#### Декоратор с параметрами
```python
def retry(max_attempts: int = 3) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
        return wrapper  # type: ignore
    return decorator
```

#### Универсальный декоратор (sync + async)
```python
def timer(func: F) -> F:
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            print(f"Время: {time.perf_counter() - start:.4f}s")
            return result
        return async_wrapper  # type: ignore
    else:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            print(f"Время: {time.perf_counter() - start:.4f}s")
            return result
        return sync_wrapper  # type: ignore
```

### 2. Продвинутые Type Hints

#### Generic типы
```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()

# Использование
int_stack: Stack[int] = Stack()
str_stack: Stack[str] = Stack()
```

#### Protocols (структурная типизация)
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> str: ...
    
    @property
    def area(self) -> float: ...

class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius
    
    def draw(self) -> str:
        return f"Circle({self.radius})"
    
    @property
    def area(self) -> float:
        return 3.14 * self.radius ** 2

# Circle автоматически соответствует Drawable!
def render(shape: Drawable) -> None:
    print(shape.draw())

circle = Circle(5)
render(circle)  # Работает!
```

#### Union и Literal
```python
from typing import Union, Literal

# Union - один из типов
ID = Union[int, str]

# Literal - конкретные значения
Status = Literal["pending", "completed", "failed"]
HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]

def process_request(method: HttpMethod, status: Status) -> None:
    # IDE знает точные возможные значения!
    pass
```

#### TypedDict
```python
from typing import TypedDict, Optional

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    age: Optional[int]

# Использование как обычный dict, но с проверкой типов
user: UserDict = {
    "id": 1,
    "name": "John",
    "email": "john@example.com",
    "age": 30
}
```

#### Callable типы
```python
from typing import Callable

# Функция, принимающая int и возвращающая str
Processor = Callable[[int], str]

def apply_processor(data: List[int], proc: Processor) -> List[str]:
    return [proc(item) for item in data]

# Использование
result = apply_processor([1, 2, 3], lambda x: f"Item {x}")
```

### 3. Комбинирование декораторов и типов

```python
from typing import TypeVar, Callable, Any, cast
import functools

F = TypeVar('F', bound=Callable[..., Any])

def validate_types(func: F) -> F:
    """Декоратор для валидации типов во время выполнения"""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Получаем аннотации типов
        hints = get_type_hints(func)
        
        # Валидируем аргументы
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        
        for name, value in bound.arguments.items():
            if name in hints:
                expected_type = hints[name]
                if not isinstance(value, expected_type):
                    raise TypeError(f"Аргумент {name} должен быть {expected_type}")
        
        return func(*args, **kwargs)
    
    return cast(F, wrapper)

# Использование
@validate_types
def add_numbers(a: int, b: int) -> int:
    return a + b
```

## 🔥 Практические паттерны

### 1. Декоратор-класс
```python
class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls: List[float] = []
    
    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            # Очищаем старые вызовы
            self.calls = [call for call in self.calls if now - call < self.period]
            
            if len(self.calls) >= self.max_calls:
                raise Exception("Rate limit exceeded")
            
            self.calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper  # type: ignore

# Использование
@RateLimiter(max_calls=5, period=60.0)  # 5 вызовов в минуту
def api_call() -> str:
    return "API response"
```

### 2. Context Manager + Generic
```python
from typing import ContextManager, TypeVar, Generic
from contextlib import contextmanager

T = TypeVar('T')

class ResourceManager(Generic[T]):
    def __init__(self, resource: T) -> None:
        self.resource = resource
    
    def __enter__(self) -> T:
        print(f"Acquiring {type(self.resource).__name__}")
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        print(f"Releasing {type(self.resource).__name__}")

# Использование
with ResourceManager("database_connection") as db:
    print(f"Using {db}")
```

### 3. Async декораторы с типизацией
```python
from typing import Awaitable, TypeVar, Callable

AsyncF = TypeVar('AsyncF', bound=Callable[..., Awaitable[Any]])

def async_retry(max_attempts: int = 3) -> Callable[[AsyncF], AsyncF]:
    def decorator(func: AsyncF) -> AsyncF:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        return wrapper  # type: ignore
    return decorator
```

## ⚡ Лучшие практики

### Type Hints
- ✅ Используй `from __future__ import annotations` для forward references
- ✅ Предпочитай `list[int]` вместо `List[int]` (Python 3.9+)
- ✅ Используй `Optional[T]` вместо `Union[T, None]`
- ✅ Применяй `Protocol` для duck typing
- ❌ Не злоупотребляй `Any` - лучше `object`

### Декораторы
- ✅ Всегда используй `@functools.wraps`
- ✅ Поддерживай и sync, и async функции
- ✅ Добавляй методы для управления (cache_clear, stats)
- ✅ Делай декораторы композируемыми
- ❌ Не изменяй сигнатуру функции без необходимости

## 🎯 Следующий шаг: FastAPI (13:00-15:00)

Готов к созданию современного API с автоматической документацией? 🚀