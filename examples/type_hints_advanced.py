"""
Продвинутые Type Hints в Python
Изучаем: Generic, Protocol, Union, Literal, TypedDict, и многое другое
"""

from typing import (
    # Основные типы
    List, Dict, Set, Tuple, Optional, Union, Any, Callable,
    # Продвинутые типы
    TypeVar, Generic, Protocol, runtime_checkable,
    # Специальные типы
    Literal, Final, ClassVar, TypedDict, NamedTuple,
    # Для работы с функциями
    Awaitable, Coroutine, AsyncGenerator, Generator,
    # Для валидации
    get_type_hints, get_origin, get_args
)
from typing_extensions import Self, ParamSpec, Concatenate
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from collections.abc import Sequence, Mapping
import json


# 1. GENERIC ТИПЫ
T = TypeVar('T')  # Любой тип
K = TypeVar('K')  # Key type
V = TypeVar('V')  # Value type
P = ParamSpec('P')  # Parameters


class Stack(Generic[T]):
    """Типизированный стек"""
    
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        """Добавить элемент"""
        self._items.append(item)
    
    def pop(self) -> T:
        """Извлечь элемент"""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def peek(self) -> Optional[T]:
        """Посмотреть верхний элемент"""
        return self._items[-1] if self._items else None
    
    def is_empty(self) -> bool:
        """Проверить пустоту"""
        return len(self._items) == 0
    
    def size(self) -> int:
        """Размер стека"""
        return len(self._items)
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __iter__(self) -> Generator[T, None, None]:
        """Итерация по стеку (сверху вниз)"""
        for item in reversed(self._items):
            yield item


class Cache(Generic[K, V]):
    """Типизированный кэш"""
    
    def __init__(self, max_size: int = 100) -> None:
        self._data: Dict[K, V] = {}
        self._max_size = max_size
    
    def get(self, key: K) -> Optional[V]:
        """Получить значение по ключу"""
        return self._data.get(key)
    
    def set(self, key: K, value: V) -> None:
        """Установить значение"""
        if len(self._data) >= self._max_size and key not in self._data:
            # Удаляем первый элемент (простая стратегия)
            first_key = next(iter(self._data))
            del self._data[first_key]
        
        self._data[key] = value
    
    def delete(self, key: K) -> bool:
        """Удалить ключ"""
        if key in self._data:
            del self._data[key]
            return True
        return False
    
    def clear(self) -> None:
        """Очистить кэш"""
        self._data.clear()
    
    def keys(self) -> List[K]:
        """Получить все ключи"""
        return list(self._data.keys())
    
    def values(self) -> List[V]:
        """Получить все значения"""
        return list(self._data.values())


# 2. PROTOCOLS - Структурная типизация
@runtime_checkable
class Drawable(Protocol):
    """Протокол для объектов, которые можно рисовать"""
    
    def draw(self) -> str:
        """Нарисовать объект"""
        ...
    
    @property
    def area(self) -> float:
        """Площадь объекта"""
        ...


@runtime_checkable
class Serializable(Protocol):
    """Протокол для сериализуемых объектов"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        """Создать из словаря"""
        ...


class Circle:
    """Круг - реализует Drawable"""
    
    def __init__(self, radius: float) -> None:
        self.radius = radius
    
    def draw(self) -> str:
        return f"Круг радиусом {self.radius}"
    
    @property
    def area(self) -> float:
        return 3.14159 * self.radius ** 2


class Rectangle:
    """Прямоугольник - реализует Drawable и Serializable"""
    
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
    
    def draw(self) -> str:
        return f"Прямоугольник {self.width}x{self.height}"
    
    @property
    def area(self) -> float:
        return self.width * self.height
    
    def to_dict(self) -> Dict[str, Any]:
        return {"width": self.width, "height": self.height}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        return cls(data["width"], data["height"])


# 3. UNION И LITERAL ТИПЫ
class Status(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Literal для ограничения значений
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

# Union для альтернативных типов
ID = Union[int, str]  # ID может быть числом или строкой
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


# 4. TYPEDDICT ДЛЯ СТРУКТУРИРОВАННЫХ СЛОВАРЕЙ
class UserDict(TypedDict):
    """Типизированный словарь пользователя"""
    id: int
    name: str
    email: str
    age: Optional[int]
    is_active: bool


class ConfigDict(TypedDict, total=False):  # total=False - все поля опциональные
    """Конфигурация (все поля опциональные)"""
    host: str
    port: int
    debug: bool
    timeout: float


# 5. NAMEDTUPLE С ТИПАМИ
class Point(NamedTuple):
    """Точка в 2D пространстве"""
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """Расстояние до другой точки"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Color(NamedTuple):
    """RGB цвет"""
    red: int
    green: int
    blue: int
    alpha: float = 1.0
    
    def to_hex(self) -> str:
        """Преобразовать в HEX"""
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"


# 6. DATACLASS С ПРОДВИНУТОЙ ТИПИЗАЦИЕЙ
@dataclass(frozen=True)  # Неизменяемый dataclass
class Product:
    """Продукт в магазине"""
    id: int
    name: str
    price: float
    category: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # ClassVar - переменная класса, не экземпляра
    _next_id: ClassVar[int] = 1
    
    def __post_init__(self) -> None:
        """Валидация после создания"""
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if not self.name.strip():
            raise ValueError("Название не может быть пустым")


@dataclass
class Order:
    """Заказ"""
    id: int
    user_id: int
    products: List[Product]
    status: Status = Status.PENDING
    created_at: Optional[str] = None
    
    @property
    def total_price(self) -> float:
        """Общая стоимость заказа"""
        return sum(product.price for product in self.products)
    
    def add_product(self, product: Product) -> None:
        """Добавить продукт"""
        self.products.append(product)
    
    def remove_product(self, product_id: int) -> bool:
        """Удалить продукт по ID"""
        for i, product in enumerate(self.products):
            if product.id == product_id:
                del self.products[i]
                return True
        return False


# 7. ФУНКЦИИ С ПРОДВИНУТОЙ ТИПИЗАЦИЕЙ
def process_items(
    items: Sequence[T],  # Sequence - более общий тип чем List
    processor: Callable[[T], V],  # Функция обработки
    filter_func: Optional[Callable[[T], bool]] = None  # Опциональный фильтр
) -> List[V]:
    """
    Обработать элементы с помощью функции
    
    Args:
        items: Последовательность элементов
        processor: Функция обработки каждого элемента
        filter_func: Опциональная функция фильтрации
    
    Returns:
        Список обработанных элементов
    """
    filtered_items = items
    if filter_func:
        filtered_items = [item for item in items if filter_func(item)]
    
    return [processor(item) for item in filtered_items]


def create_cache_factory() -> Callable[[], Cache[str, Any]]:
    """Фабрика для создания кэшей"""
    def factory() -> Cache[str, Any]:
        return Cache[str, Any](max_size=50)
    return factory


# Overload для функций с разными сигнатурами
from typing import overload

@overload
def get_user_info(user_id: int) -> UserDict:
    ...

@overload  
def get_user_info(user_id: str) -> UserDict:
    ...

def get_user_info(user_id: ID) -> UserDict:
    """Получить информацию о пользователе по ID"""
    # В реальности здесь был бы запрос к БД
    return UserDict(
        id=int(user_id) if isinstance(user_id, str) else user_id,
        name="Test User",
        email="test@example.com",
        age=25,
        is_active=True
    )


# 8. АСИНХРОННЫЕ ТИПЫ
async def fetch_data(url: str) -> Dict[str, Any]:
    """Асинхронное получение данных"""
    # Имитация HTTP запроса
    await asyncio.sleep(0.1)
    return {"url": url, "status": "success"}


async def process_urls(urls: List[str]) -> AsyncGenerator[Dict[str, Any], None]:
    """Асинхронный генератор для обработки URL"""
    for url in urls:
        data = await fetch_data(url)
        yield data


# 9. ФУНКЦИИ ДЛЯ РАБОТЫ С ТИПАМИ
def analyze_type(obj: Any) -> Dict[str, Any]:
    """Анализ типа объекта"""
    obj_type = type(obj)
    
    return {
        "type": obj_type.__name__,
        "module": obj_type.__module__,
        "mro": [cls.__name__ for cls in obj_type.__mro__],
        "is_generic": hasattr(obj_type, "__origin__"),
        "origin": getattr(obj_type, "__origin__", None),
        "args": getattr(obj_type, "__args__", ()),
    }


def validate_protocol(obj: Any, protocol: type) -> bool:
    """Проверить соответствие объекта протоколу"""
    return isinstance(obj, protocol)


# ДЕМОНСТРАЦИЯ
def demo_type_hints() -> None:
    """Демонстрация продвинутых type hints"""
    print("🔍 ДЕМОНСТРАЦИЯ ПРОДВИНУТЫХ TYPE HINTS\n")
    
    # 1. Generic типы
    print("1️⃣ Generic типы:")
    int_stack: Stack[int] = Stack()
    int_stack.push(1)
    int_stack.push(2)
    int_stack.push(3)
    
    print(f"Стек: {list(int_stack)}")
    print(f"Верхний элемент: {int_stack.peek()}")
    
    str_cache: Cache[str, str] = Cache()
    str_cache.set("key1", "value1")
    str_cache.set("key2", "value2")
    print(f"Кэш: {str_cache.get('key1')}")
    print()
    
    # 2. Protocols
    print("2️⃣ Protocols:")
    circle = Circle(5.0)
    rectangle = Rectangle(4.0, 3.0)
    
    shapes: List[Drawable] = [circle, rectangle]
    for shape in shapes:
        print(f"{shape.draw()}, площадь: {shape.area}")
    
    print(f"Circle is Drawable: {validate_protocol(circle, Drawable)}")
    print(f"Rectangle is Serializable: {validate_protocol(rectangle, Serializable)}")
    print()
    
    # 3. TypedDict
    print("3️⃣ TypedDict:")
    user: UserDict = {
        "id": 1,
        "name": "Иван Петров",
        "email": "ivan@example.com",
        "age": 30,
        "is_active": True
    }
    print(f"Пользователь: {user['name']}, возраст: {user['age']}")
    
    config: ConfigDict = {"host": "localhost", "port": 8000}
    print(f"Конфигурация: {config}")
    print()
    
    # 4. NamedTuple и dataclass
    print("4️⃣ NamedTuple и dataclass:")
    point1 = Point(0.0, 0.0)
    point2 = Point(3.0, 4.0)
    print(f"Расстояние между точками: {point1.distance_to(point2)}")
    
    color = Color(255, 128, 0)
    print(f"Цвет: {color.to_hex()}")
    
    product = Product(1, "Ноутбук", 50000.0, "Электроника", ["компьютер", "работа"])
    order = Order(1, 123, [product])
    print(f"Заказ на сумму: {order.total_price}")
    print()
    
    # 5. Функции с типизацией
    print("5️⃣ Функции с типизацией:")
    numbers = [1, 2, 3, 4, 5]
    squared = process_items(
        numbers,
        lambda x: x ** 2,
        lambda x: x % 2 == 0  # Только четные
    )
    print(f"Квадраты четных чисел: {squared}")
    
    user_info = get_user_info(123)
    print(f"Информация о пользователе: {user_info['name']}")
    print()
    
    # 6. Анализ типов
    print("6️⃣ Анализ типов:")
    cache_analysis = analyze_type(str_cache)
    print(f"Анализ кэша: {cache_analysis}")


async def demo_async_types() -> None:
    """Демонстрация асинхронных типов"""
    print("7️⃣ Асинхронные типы:")
    
    urls = ["http://example.com", "http://google.com", "http://github.com"]
    
    async for data in process_urls(urls):
        print(f"Обработан URL: {data}")


if __name__ == "__main__":
    demo_type_hints()
    print("\n" + "="*50)
    asyncio.run(demo_async_types())