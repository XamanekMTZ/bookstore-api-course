"""
Middleware для BookStore API
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logging_config import (
    set_request_context, 
    clear_request_context, 
    log_api_request,
    get_logger
)
from .config import settings


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("bookstore.middleware")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Генерируем уникальный ID для запроса
        request_id = str(uuid.uuid4())
        
        # Получаем информацию о запросе
        start_time = time.time()
        method = request.method
        url = str(request.url)
        path = request.url.path
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else "unknown"
        
        # Устанавливаем контекст для логирования
        set_request_context(request_id)
        
        # Добавляем request_id в headers ответа
        response = None
        status_code = 500
        error_message = None
        
        try:
            # Логируем начало запроса
            self.logger.info(f"Request started: {method} {path}", extra={
                'extra_fields': {
                    'request_id': request_id,
                    'method': method,
                    'path': path,
                    'url': url,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'event_type': 'request_start'
                }
            })
            
            # Выполняем запрос
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            error_message = str(e)
            status_code = 500
            
            self.logger.error(f"Request failed: {method} {path}", extra={
                'extra_fields': {
                    'request_id': request_id,
                    'method': method,
                    'path': path,
                    'error': error_message,
                    'event_type': 'request_error'
                }
            }, exc_info=True)
            
            # Возвращаем JSON ошибку
            response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "request_id": request_id,
                    "message": "An unexpected error occurred"
                }
            )
        
        finally:
            # Вычисляем время выполнения
            duration_ms = (time.time() - start_time) * 1000
            
            # Добавляем headers в ответ
            if response:
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            # Логируем завершение запроса
            log_api_request(
                endpoint=path,
                method=method,
                status_code=status_code,
                duration_ms=duration_ms,
                error=error_message
            )
            
            # Очищаем контекст
            clear_request_context()
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("bookstore.ratelimit")
        self.requests = {}  # Простое in-memory хранилище (в production использовать Redis)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.is_production:
            # В development режиме пропускаем rate limiting
            return await call_next(request)
        
        ip_address = request.client.host if request.client else "unknown"
        path = request.url.path
        current_time = time.time()
        
        # Определяем лимит в зависимости от endpoint
        if path.startswith("/auth/"):
            rate_limit = settings.auth_rate_limit_per_minute
        else:
            rate_limit = settings.rate_limit_per_minute
        
        # Ключ для отслеживания запросов
        key = f"{ip_address}:{path}"
        
        # Очищаем старые записи (старше 1 минуты)
        if key in self.requests:
            self.requests[key] = [
                timestamp for timestamp in self.requests[key]
                if current_time - timestamp < 60
            ]
        else:
            self.requests[key] = []
        
        # Проверяем лимит
        if len(self.requests[key]) >= rate_limit:
            self.logger.warning(f"Rate limit exceeded for {ip_address}", extra={
                'extra_fields': {
                    'ip_address': ip_address,
                    'path': path,
                    'requests_count': len(self.requests[key]),
                    'rate_limit': rate_limit,
                    'event_type': 'rate_limit_exceeded'
                }
            })
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded. Maximum {rate_limit} requests per minute.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Добавляем текущий запрос
        self.requests[key].append(current_time)
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления security headers"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Добавляем security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        }
        
        # В production добавляем HSTS
        if settings.is_production:
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware для сбора метрик (упрощенная версия)"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("bookstore.metrics")
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_endpoint": {},
            "response_times": []
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.metrics_enabled:
            return await call_next(request)
        
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        response = await call_next(request)
        
        duration_ms = (time.time() - start_time) * 1000
        status_code = response.status_code
        
        # Обновляем метрики
        self.metrics["requests_total"] += 1
        
        if status_code not in self.metrics["requests_by_status"]:
            self.metrics["requests_by_status"][status_code] = 0
        self.metrics["requests_by_status"][status_code] += 1
        
        endpoint_key = f"{method} {path}"
        if endpoint_key not in self.metrics["requests_by_endpoint"]:
            self.metrics["requests_by_endpoint"][endpoint_key] = 0
        self.metrics["requests_by_endpoint"][endpoint_key] += 1
        
        self.metrics["response_times"].append(duration_ms)
        
        # Ограничиваем размер массива времен ответа
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]
        
        # Логируем метрики каждые 100 запросов
        if self.metrics["requests_total"] % 100 == 0:
            avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            
            self.logger.info("Metrics update", extra={
                'extra_fields': {
                    'total_requests': self.metrics["requests_total"],
                    'avg_response_time_ms': round(avg_response_time, 2),
                    'status_codes': self.metrics["requests_by_status"],
                    'event_type': 'metrics_update'
                }
            })
        
        return response
    
    def get_metrics(self) -> dict:
        """Получение текущих метрик"""
        if not self.metrics["response_times"]:
            return self.metrics
        
        response_times = self.metrics["response_times"]
        return {
            **self.metrics,
            "avg_response_time_ms": round(sum(response_times) / len(response_times), 2),
            "min_response_time_ms": round(min(response_times), 2),
            "max_response_time_ms": round(max(response_times), 2),
        }