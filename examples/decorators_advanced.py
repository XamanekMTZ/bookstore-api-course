"""
Продвинутые декораторы + Type Hints
Изучаем: собственные декораторы, functools, typing, generics
"""

import time
import functools
import logging
from typing import (
    TypeVar, Generic, Callable, Any, Dict, List, Optional, 
    Union, Tuple, Protocol, runtime_checkable
)
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import inspect


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Type Variables для Generic типов
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])
R = TypeVar('R')  # Return type


# 1. ДЕКОРАТОР ЗАМЕРА ВРЕМЕНИ
def timer(func: F) -> F:
    """
    Декоратор для замера времени выполнения функции
    Поддерживает как синхронные, так и асинхронные функции
    """
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                logger.info(f"⏱️ {func.__name__} выполнилась за {execution_time:.4f} секунд")
        return async_wrapper  # type: ignore
    else:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                logger.info(f"⏱️ {func.__name__} выполнилась за {execution_time:.4f} секунд")
        return sync_wrapper  # type: ignore


# 2. ДЕКОРАТОР ПОВТОРА ПРИ ОШИБКАХ
def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[type, ...] = (Exception,)
) -> Callable[[F], F]:
    """
    Декоратор для повтора функции при ошибках
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Множитель для увеличения задержки
        exceptions: Типы исключений для повтора
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts - 1:  # Последняя попытка
                        logger.error(f"❌ {func.__name__} не удалось выполнить за {max_attempts} попыток")
                        raise e
                    
                    logger.warning(f"🔄 {func.__name__} попытка {attempt + 1} не удалась: {e}")
                    logger.info(f"⏳ Ожидание {current_delay:.2f} секунд...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # Этот код никогда не должен выполниться, но для типизации
            if last_exception:
                raise last_exception
                
        return wrapper  # type: ignore
    return decorator


# 3. ПРОДВИНУТЫЙ КЭШИРУЮЩИЙ ДЕКОРАТОР
class CacheStats:
    """Статистика кэша"""
    def __init__(self) -> None:
        self.hits: int = 0
        self.misses: int = 0
        self.cache_size: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    def __str__(self) -> str:
        return f"Cache(hits={self.hits}, misses={self.misses}, hit_rate={self.hit_rate:.1f}%, size={self.cache_size})"


def cache(
    maxsize: Optional[int] = 128,
    ttl: Optional[float] = None,
    typed: bool = False
) -> Callable[[F], F]:
    """
    Продвинутый кэширующий декоратор
    
    Args:
        maxsize: Максимальный размер кэша (None = безлимитный)
        ttl: Время жизни записи в секундах (None = бессрочно)
        typed: Различать типы аргументов (True/False)
    """
    def decorator(func: F) -> F:
        cache_data: Dict[str, Tuple[Any, float]] = {}
        stats = CacheStats()
        
        def make_key(*args: Any, **kwargs: Any) -> str:
            """Создание ключа для кэша"""
            key_parts = []
            
            # Добавляем позиционные аргументы
            for arg in args:
                if typed:
                    key_parts.append(f"{type(arg).__name__}:{arg}")
                else:
                    key_parts.append(str(arg))
            
            # Добавляем именованные аргументы
            for k, v in sorted(kwargs.items()):
                if typed:
                    key_parts.append(f"{k}={type(v).__name__}:{v}")
                else:
                    key_parts.append(f"{k}={v}")
            
            return "|".join(key_parts)
        
        def is_expired(timestamp: float) -> bool:
            """Проверка истечения TTL"""
            if ttl is None:
                return False
            return time.time() - timestamp > ttl
        
        def cleanup_expired() -> None:
            """Очистка истекших записей"""
            if ttl is None:
                return
            
            current_time = time.time()
            expired_keys = [
                key for key, (_, timestamp) in cache_data.items()
                if current_time - timestamp > ttl
            ]
            
            for key in expired_keys:
                del cache_data[key]
            
            stats.cache_size = len(cache_data)
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Очистка истекших записей
            cleanup_expired()
            
            # Создание ключа
            cache_key = make_key(*args, **kwargs)
            
            # Проверка наличия в кэше
            if cache_key in cache_data:
                value, timestamp = cache_data[cache_key]
                if not is_expired(timestamp):
                    stats.hits += 1
                    logger.debug(f"💾 Cache HIT для {func.__name__}")
                    return value
                else:
                    # Удаляем истекшую запись
                    del cache_data[cache_key]
            
            # Вычисление значения
            stats.misses += 1
            logger.debug(f"🔍 Cache MISS для {func.__name__}")
            result = func(*args, **kwargs)
            
            # Сохранение в кэш
            current_time = time.time()
            cache_data[cache_key] = (result, current_time)
            
            # Проверка размера кэша
            if maxsize is not None and len(cache_data) > maxsize:
                # Удаляем самую старую запись (простая стратегия)
                oldest_key = min(cache_data.keys(), 
                               key=lambda k: cache_data[k][1])
                del cache_data[oldest_key]
            
            stats.cache_size = len(cache_data)
            return result
        
        # Добавляем методы для управления кэшем
        wrapper.cache_info = lambda: stats  # type: ignore
        wrapper.cache_clear = lambda: cache_data.clear()  # type: ignore
        
        return wrapper  # type: ignore
    return decorator


# 4. ДЕКОРАТОР ВАЛИДАЦИИ С ПРОТОКОЛАМИ
@runtime_checkable
class Validator(Protocol):
    """Протокол для валидаторов"""
    def validate(self, value: Any) -> bool:
        ...
    
    def get_error_message(self, value: Any) -> str:
        ...


class RangeValidator:
    """Валидатор диапазона чисел"""
    def __init__(self, min_val: float, max_val: float) -> None:
        self.min_val = min_val
        self.max_val = max_val
    
    def validate(self, value: Any) -> bool:
        return isinstance(value, (int, float)) and self.min_val <= value <= self.max_val
    
    def get_error_message(self, value: Any) -> str:
        return f"Значение {value} должно быть в диапазоне [{self.min_val}, {self.max_val}]"


class TypeValidator:
    """Валидатор типов"""
    def __init__(self, expected_type: type) -> None:
        self.expected_type = expected_type
    
    def validate(self, value: Any) -> bool:
        return isinstance(value, self.expected_type)
    
    def get_error_message(self, value: Any) -> str:
        return f"Ожидался тип {self.expected_type.__name__}, получен {type(value).__name__}"


def validate_args(**validators: Validator) -> Callable[[F], F]:
    """
    Декоратор для валидации аргументов функции
    
    Usage:
        @validate_args(
            age=RangeValidator(0, 150),
            name=TypeValidator(str)
        )
        def create_user(name: str, age: int) -> User:
            ...
    """
    def decorator(func: F) -> F:
        # Получаем информацию о параметрах функции
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Создаем словарь всех аргументов
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Валидируем каждый аргумент
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not validator.validate(value):
                        error_msg = validator.get_error_message(value)
                        raise ValueError(f"Валидация параметра '{param_name}' не прошла: {error_msg}")
            
            return func(*args, **kwargs)
        
        return wrapper  # type: ignore
    return decorator


# 5. ДЕКОРАТОР ЛОГИРОВАНИЯ С КОНТЕКСТОМ
def log_calls(
    level: int = logging.INFO,
    include_args: bool = True,
    include_result: bool = True,
    max_arg_length: int = 100
) -> Callable[[F], F]:
    """
    Декоратор для логирования вызовов функций
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Подготовка информации об аргументах
            args_info = ""
            if include_args:
                args_str = ", ".join([
                    str(arg)[:max_arg_length] + ("..." if len(str(arg)) > max_arg_length else "")
                    for arg in args
                ])
                kwargs_str = ", ".join([
                    f"{k}={str(v)[:max_arg_length]}" + ("..." if len(str(v)) > max_arg_length else "")
                    for k, v in kwargs.items()
                ])
                all_args = [args_str, kwargs_str] if args_str and kwargs_str else [args_str or kwargs_str]
                args_info = f"({', '.join(filter(None, all_args))})"
            
            logger.log(level, f"🔵 Вызов {func.__name__}{args_info}")
            
            try:
                result = func(*args, **kwargs)
                
                if include_result:
                    result_str = str(result)[:max_arg_length]
                    if len(str(result)) > max_arg_length:
                        result_str += "..."
                    logger.log(level, f"✅ {func.__name__} вернула: {result_str}")
                else:
                    logger.log(level, f"✅ {func.__name__} выполнена успешно")
                
                return result
            
            except Exception as e:
                logger.log(logging.ERROR, f"❌ {func.__name__} вызвала исключение: {e}")
                raise
        
        return wrapper  # type: ignore
    return decorator


# ДЕМОНСТРАЦИЯ ВСЕХ ДЕКОРАТОРОВ
class MathOperations:
    """Класс для демонстрации декораторов"""
    
    @timer
    @cache(maxsize=50, ttl=10.0)
    @log_calls(include_result=True)
    def fibonacci(self, n: int) -> int:
        """Вычисление числа Фибоначчи с кэшированием"""
        if n <= 1:
            return n
        return self.fibonacci(n - 1) + self.fibonacci(n - 2)
    
    @retry(max_attempts=3, delay=0.1, exceptions=(ValueError, ZeroDivisionError))
    @validate_args(
        a=TypeValidator(float),
        b=TypeValidator(float)
    )
    @timer
    def divide(self, a: float, b: float) -> float:
        """Деление с повтором при ошибках"""
        if b == 0:
            raise ZeroDivisionError("Деление на ноль!")
        return a / b
    
    @cache(maxsize=10)
    @validate_args(
        base=RangeValidator(1, 1000),
        exponent=RangeValidator(0, 10)
    )
    def power(self, base: float, exponent: float) -> float:
        """Возведение в степень с валидацией"""
        time.sleep(0.1)  # Имитация тяжелых вычислений
        return base ** exponent


# Асинхронные функции с декораторами
@timer
async def async_operation(duration: float) -> str:
    """Асинхронная операция с замером времени"""
    await asyncio.sleep(duration)
    return f"Операция завершена за {duration} секунд"


def demo_decorators() -> None:
    """Демонстрация всех декораторов"""
    print("🎭 ДЕМОНСТРАЦИЯ ПРОДВИНУТЫХ ДЕКОРАТОРОВ\n")
    
    math_ops = MathOperations()
    
    # 1. Кэширование + логирование
    print("1️⃣ Кэширование Фибоначчи:")
    print(f"fibonacci(10) = {math_ops.fibonacci(10)}")
    print(f"fibonacci(10) = {math_ops.fibonacci(10)}")  # Из кэша
    print(f"Cache info: {math_ops.fibonacci.cache_info()}")
    print()
    
    # 2. Валидация + повтор
    print("2️⃣ Валидация и повтор:")
    try:
        result = math_ops.divide(10.0, 2.0)
        print(f"10 / 2 = {result}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    try:
        math_ops.divide("10", 2.0)  # Ошибка типа
    except ValueError as e:
        print(f"Ошибка валидации: {e}")
    print()
    
    # 3. Валидация диапазона
    print("3️⃣ Валидация диапазона:")
    try:
        result = math_ops.power(2.0, 3.0)
        print(f"2^3 = {result}")
        result = math_ops.power(2.0, 3.0)  # Из кэша
        print(f"2^3 = {result} (из кэша)")
    except ValueError as e:
        print(f"Ошибка валидации: {e}")
    
    try:
        math_ops.power(2000.0, 3.0)  # Вне диапазона
    except ValueError as e:
        print(f"Ошибка валидации: {e}")
    print()


async def demo_async_decorators() -> None:
    """Демонстрация асинхронных декораторов"""
    print("4️⃣ Асинхронные декораторы:")
    result = await async_operation(0.5)
    print(f"Результат: {result}")


if __name__ == "__main__":
    # Синхронная демонстрация
    demo_decorators()
    
    # Асинхронная демонстрация
    print("\n" + "="*50)
    asyncio.run(demo_async_decorators())