"""
Система структурированного логирования для BookStore API
"""

import logging
import json
import sys
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar
from functools import wraps

from .config import settings

# Context variables для отслеживания request ID
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class JSONFormatter(logging.Formatter):
    """Форматтер для структурированных JSON логов"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Форматирование записи лога в JSON"""
        
        # Базовая структура лога
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "bookstore-api",
            "version": settings.app_version,
            "environment": settings.environment,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Добавляем request ID если доступен
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        # Добавляем user ID если доступен
        user_id = user_id_var.get()
        if user_id:
            log_entry["user_id"] = user_id
        
        # Добавляем информацию о модуле и функции
        if record.pathname:
            log_entry["module"] = record.module
            log_entry["function"] = record.funcName
            log_entry["line"] = record.lineno
        
        # Добавляем дополнительные поля из extra
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Обработка исключений
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Добавляем метрики производительности если есть
        if hasattr(record, 'duration_ms'):
            log_entry["duration_ms"] = record.duration_ms
        
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        
        return json.dumps(log_entry, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Простой текстовый форматтер для development"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Форматирование записи лога в текстовом виде"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Базовое сообщение
        message = f"[{timestamp}] {record.levelname:8} | {record.name:20} | {record.getMessage()}"
        
        # Добавляем request ID если есть
        request_id = request_id_var.get()
        if request_id:
            message += f" | req_id={request_id[:8]}"
        
        # Добавляем user ID если есть
        user_id = user_id_var.get()
        if user_id:
            message += f" | user_id={user_id}"
        
        # Добавляем информацию о производительности
        if hasattr(record, 'duration_ms'):
            message += f" | {record.duration_ms}ms"
        
        if hasattr(record, 'status_code'):
            message += f" | {record.status_code}"
        
        return message


def setup_logging():
    """Настройка системы логирования"""
    
    # Определяем уровень логирования
    log_level = getattr(logging, settings.log_level.upper())
    
    # Создаем root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Удаляем существующие handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Создаем handler для stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Выбираем форматтер в зависимости от настроек
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Настраиваем логирование в файл если указан
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(JSONFormatter())  # Файлы всегда в JSON
        root_logger.addHandler(file_handler)
    
    # Настраиваем уровни для внешних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Создаем logger для приложения
    app_logger = logging.getLogger("bookstore")
    app_logger.info("Logging system initialized", extra={
        'extra_fields': {
            'log_level': settings.log_level,
            'log_format': settings.log_format,
            'environment': settings.environment
        }
    })
    
    return app_logger


def get_logger(name: str = "bookstore") -> logging.Logger:
    """Получение logger с заданным именем"""
    return logging.getLogger(name)


def set_request_context(request_id: str, user_id: Optional[str] = None):
    """Установка контекста запроса для логирования"""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)


def clear_request_context():
    """Очистка контекста запроса"""
    request_id_var.set(None)
    user_id_var.set(None)


def log_performance(func):
    """Декоратор для логирования производительности функций"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger(f"bookstore.performance.{func.__module__}")
        start_time = datetime.utcnow()
        
        try:
            result = await func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(f"Function {func.__name__} completed", extra={
                'extra_fields': {
                    'function': func.__name__,
                    'module': func.__module__,
                    'duration_ms': round(duration, 2),
                    'status': 'success'
                }
            })
            
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.error(f"Function {func.__name__} failed", extra={
                'extra_fields': {
                    'function': func.__name__,
                    'module': func.__module__,
                    'duration_ms': round(duration, 2),
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            }, exc_info=True)
            
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger(f"bookstore.performance.{func.__module__}")
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(f"Function {func.__name__} completed", extra={
                'extra_fields': {
                    'function': func.__name__,
                    'module': func.__module__,
                    'duration_ms': round(duration, 2),
                    'status': 'success'
                }
            })
            
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.error(f"Function {func.__name__} failed", extra={
                'extra_fields': {
                    'function': func.__name__,
                    'module': func.__module__,
                    'duration_ms': round(duration, 2),
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            }, exc_info=True)
            
            raise
    
    # Возвращаем соответствующий wrapper в зависимости от типа функции
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class LoggerMixin:
    """Mixin для добавления логирования в классы"""
    
    @property
    def logger(self) -> logging.Logger:
        """Получение logger для класса"""
        return get_logger(f"bookstore.{self.__class__.__module__}.{self.__class__.__name__}")


def log_api_request(endpoint: str, method: str, status_code: int, duration_ms: float, 
                   user_id: Optional[str] = None, error: Optional[str] = None):
    """Логирование API запроса"""
    logger = get_logger("bookstore.api")
    
    extra_fields = {
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'duration_ms': round(duration_ms, 2),
        'request_type': 'api'
    }
    
    if user_id:
        extra_fields['user_id'] = user_id
    
    if error:
        extra_fields['error'] = error
    
    if status_code >= 500:
        logger.error(f"API request failed: {method} {endpoint}", extra={'extra_fields': extra_fields})
    elif status_code >= 400:
        logger.warning(f"API request error: {method} {endpoint}", extra={'extra_fields': extra_fields})
    else:
        logger.info(f"API request: {method} {endpoint}", extra={'extra_fields': extra_fields})


def log_database_query(query: str, duration_ms: float, rows_affected: Optional[int] = None, 
                      error: Optional[str] = None):
    """Логирование запроса к базе данных"""
    logger = get_logger("bookstore.database")
    
    extra_fields = {
        'query_type': 'database',
        'duration_ms': round(duration_ms, 2),
        'query': query[:200] + "..." if len(query) > 200 else query  # Обрезаем длинные запросы
    }
    
    if rows_affected is not None:
        extra_fields['rows_affected'] = rows_affected
    
    if error:
        extra_fields['error'] = error
        logger.error("Database query failed", extra={'extra_fields': extra_fields})
    else:
        logger.debug("Database query executed", extra={'extra_fields': extra_fields})


def log_authentication_attempt(username: str, success: bool, ip_address: Optional[str] = None, 
                              user_agent: Optional[str] = None):
    """Логирование попытки аутентификации"""
    logger = get_logger("bookstore.auth")
    
    extra_fields = {
        'username': username,
        'success': success,
        'event_type': 'authentication'
    }
    
    if ip_address:
        extra_fields['ip_address'] = ip_address
    
    if user_agent:
        extra_fields['user_agent'] = user_agent
    
    if success:
        logger.info(f"Successful authentication for user: {username}", extra={'extra_fields': extra_fields})
    else:
        logger.warning(f"Failed authentication attempt for user: {username}", extra={'extra_fields': extra_fields})


# Инициализация логирования при импорте модуля
logger = setup_logging()