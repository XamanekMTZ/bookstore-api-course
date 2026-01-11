"""
Система управления конфигурацией для BookStore API
"""

import os
from typing import List, Optional
from pydantic import validator, Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Основные настройки приложения"""
    
    # Application Info
    app_name: str = "BookStore API"
    app_version: str = "1.0.0"
    description: str = "Современная система управления книгами"
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Security Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    
    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        env="ALLOWED_ORIGINS"
    )
    allowed_methods: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS",
        env="ALLOWED_METHODS"
    )
    allowed_headers: str = Field(
        default="*",
        env="ALLOWED_HEADERS"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Performance Configuration
    workers: int = Field(default=4, env="WORKERS")
    max_connections: int = Field(default=100, env="MAX_CONNECTIONS")
    connection_timeout: int = Field(default=30, env="CONNECTION_TIMEOUT")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    auth_rate_limit_per_minute: int = Field(default=10, env="AUTH_RATE_LIMIT_PER_MINUTE")
    
    # Pagination
    default_page_size: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, env="MAX_PAGE_SIZE")
    
    # File Upload
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: str = Field(
        default="image/jpeg,image/png,image/webp",
        env="ALLOWED_FILE_TYPES"
    )
    
    # Cache Configuration
    cache_ttl: int = Field(default=300, env="CACHE_TTL")  # 5 minutes
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    
    # Monitoring
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Получение списка разрешенных origins"""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    @property
    def allowed_methods_list(self) -> List[str]:
        """Получение списка разрешенных методов"""
        return [method.strip() for method in self.allowed_methods.split(",") if method.strip()]
    
    @property
    def allowed_headers_list(self) -> List[str]:
        """Получение списка разрешенных заголовков"""
        if self.allowed_headers == "*":
            return ["*"]
        return [header.strip() for header in self.allowed_headers.split(",") if header.strip()]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Получение списка разрешенных типов файлов"""
        return [file_type.strip() for file_type in self.allowed_file_types.split(",") if file_type.strip()]
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Валидация уровня логирования"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator("log_format")
    def validate_log_format(cls, v):
        """Валидация формата логирования"""
        valid_formats = ["json", "text"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of: {valid_formats}")
        return v.lower()
    
    @validator("environment")
    def validate_environment(cls, v):
        """Валидация окружения"""
        valid_environments = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    @property
    def is_development(self) -> bool:
        """Проверка development окружения"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Проверка production окружения"""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Проверка testing окружения"""
        return self.environment == "testing"
    
    def get_database_config(self) -> dict:
        """Получение конфигурации базы данных"""
        return {
            "url": self.database_url,
            "echo": self.database_echo and self.is_development,
            "pool_size": 5 if self.is_development else 20,
            "max_overflow": 10 if self.is_development else 30,
            "pool_timeout": 30,
            "pool_recycle": 3600,
        }
    
    def get_redis_config(self) -> dict:
        """Получение конфигурации Redis"""
        return {
            "url": self.redis_url,
            "password": self.redis_password,
            "decode_responses": True,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True,
        }
    
    def get_cors_config(self) -> dict:
        """Получение конфигурации CORS"""
        return {
            "allow_origins": self.allowed_origins_list,
            "allow_credentials": True,
            "allow_methods": self.allowed_methods_list,
            "allow_headers": self.allowed_headers_list,
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DevelopmentSettings(Settings):
    """Настройки для разработки"""
    environment: str = "development"
    debug: bool = True
    log_level: str = "DEBUG"
    database_echo: bool = True
    
    # Более мягкие лимиты для разработки
    rate_limit_per_minute: int = 1000
    auth_rate_limit_per_minute: int = 100


class StagingSettings(Settings):
    """Настройки для staging окружения"""
    environment: str = "staging"
    debug: bool = False
    log_level: str = "INFO"
    
    # Умеренные лимиты для staging
    rate_limit_per_minute: int = 200
    auth_rate_limit_per_minute: int = 30


class ProductionSettings(Settings):
    """Настройки для production окружения"""
    environment: str = "production"
    debug: bool = False
    log_level: str = "WARNING"
    
    # Строгие лимиты для production
    rate_limit_per_minute: int = 60
    auth_rate_limit_per_minute: int = 10
    
    # Дополнительная валидация для production
    @validator("secret_key")
    def validate_production_secret_key(cls, v):
        """Валидация секретного ключа в production"""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters in production")
        if v in ["dev-secret-key", "change-me", "your-secret-key-here"]:
            raise ValueError("Must use secure secret key in production")
        return v
    
    @validator("jwt_secret_key")
    def validate_production_jwt_key(cls, v):
        """Валидация JWT ключа в production"""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters in production")
        if v in ["dev-jwt-secret", "change-me", "your-jwt-secret-here"]:
            raise ValueError("Must use secure JWT secret key in production")
        return v


class TestingSettings(Settings):
    """Настройки для тестирования"""
    environment: str = "testing"
    debug: bool = True
    log_level: str = "DEBUG"
    
    # Тестовая база данных
    database_url: str = "sqlite:///./test.db"
    
    # Отключаем внешние сервисы для тестов
    redis_url: str = "redis://localhost:6379/1"  # Отдельная БД для тестов
    cache_enabled: bool = False
    metrics_enabled: bool = False
    
    # Быстрые JWT токены для тестов
    jwt_expire_minutes: int = 5


@lru_cache()
def get_settings() -> Settings:
    """
    Получение настроек приложения с кэшированием
    Автоматически выбирает класс настроек на основе переменной ENVIRONMENT
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    settings_map = {
        "development": DevelopmentSettings,
        "staging": StagingSettings,
        "production": ProductionSettings,
        "testing": TestingSettings,
    }
    
    settings_class = settings_map.get(environment, DevelopmentSettings)
    return settings_class()


# Глобальный экземпляр настроек
settings = get_settings()


def reload_settings():
    """Перезагрузка настроек (полезно для тестов)"""
    get_settings.cache_clear()
    global settings
    settings = get_settings()
    return settings