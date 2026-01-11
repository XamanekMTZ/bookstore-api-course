# 🐳 Docker Setup для BookStore API

## Обзор

Полная контейнеризация BookStore API с использованием Docker и docker-compose для локальной разработки и production deployment.

## Структура файлов

```
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Локальная разработка
├── nginx.conf              # Reverse proxy конфигурация
├── init.sql                # Инициализация PostgreSQL
├── .dockerignore           # Исключения для Docker build
├── .env.example            # Пример переменных окружения
└── docker-build.sh         # Скрипт сборки (Linux/Mac)
```

## Быстрый старт

### 1. Подготовка окружения

```bash
# Скопировать пример конфигурации
cp .env.example .env

# Отредактировать переменные окружения
nano .env
```

### 2. Сборка и запуск

```bash
# Сборка образа
docker build -t bookstore-api:latest .

# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 3. Проверка работоспособности

```bash
# Health check
curl http://localhost:8000/health

# API документация
open http://localhost:8000/docs

# Через Nginx (порт 80)
curl http://localhost/health
```

## Архитектура контейнеров

### API Container (bookstore-api)
- **Base Image**: python:3.11-slim
- **Multi-stage build** для оптимизации размера
- **Non-root user** для безопасности
- **Health check** встроен в контейнер
- **Port**: 8000

### Database Container (PostgreSQL)
- **Image**: postgres:15-alpine
- **Persistent storage** через Docker volumes
- **Health check** с pg_isready
- **Port**: 5432

### Cache Container (Redis)
- **Image**: redis:7-alpine
- **Persistent storage** с AOF
- **Health check** с redis-cli ping
- **Port**: 6379

### Reverse Proxy (Nginx)
- **Image**: nginx:alpine
- **Rate limiting** настроен
- **Security headers** добавлены
- **Gzip compression** включен
- **Ports**: 80, 443

## Особенности Docker образа

### Multi-stage Build
```dockerfile
# Stage 1: Builder - устанавливает зависимости
FROM python:3.11-slim as builder
# ... установка зависимостей в venv

# Stage 2: Production - только runtime
FROM python:3.11-slim as production
# ... копирование venv и приложения
```

### Безопасность
- ✅ Non-root пользователь
- ✅ Минимальный base image
- ✅ Только необходимые зависимости
- ✅ Health check для мониторинга

### Оптимизация
- ✅ .dockerignore для исключения ненужных файлов
- ✅ Кэширование слоев Docker
- ✅ Виртуальное окружение Python
- ✅ Сжатие в Nginx

## Команды управления

### Разработка
```bash
# Запуск в development режиме
docker-compose up

# Пересборка после изменений
docker-compose up --build

# Просмотр логов
docker-compose logs -f api

# Подключение к контейнеру
docker-compose exec api bash
```

### Production
```bash
# Сборка production образа
docker build --target production -t bookstore-api:prod .

# Запуск с production конфигурацией
docker run -d \
  --name bookstore-api \
  -p 8000:8000 \
  --env-file .env.production \
  bookstore-api:prod
```

### Мониторинг
```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Health check
docker-compose exec api curl http://localhost:8000/health
```

## Переменные окружения

### Обязательные
- `DATABASE_URL` - URL подключения к PostgreSQL
- `SECRET_KEY` - Секретный ключ приложения
- `JWT_SECRET_KEY` - Ключ для JWT токенов

### Опциональные
- `REDIS_URL` - URL подключения к Redis (по умолчанию: redis://localhost:6379)
- `LOG_LEVEL` - Уровень логирования (по умолчанию: INFO)
- `ENVIRONMENT` - Окружение (development/staging/production)

## Volumes и данные

### Persistent Storage
- `postgres_data` - Данные PostgreSQL
- `redis_data` - Данные Redis
- `./logs` - Логи приложения

### Backup
```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U bookstore bookstore_db > backup.sql

# Restore PostgreSQL
docker-compose exec -T db psql -U bookstore bookstore_db < backup.sql
```

## Troubleshooting

### Проблемы с запуском
```bash
# Проверить логи
docker-compose logs api

# Проверить health check
docker-compose exec api curl http://localhost:8000/health

# Перезапустить сервисы
docker-compose restart
```

### Проблемы с базой данных
```bash
# Проверить подключение к БД
docker-compose exec api python -c "
from bookstore.database import engine
print(engine.execute('SELECT 1').scalar())
"

# Пересоздать БД
docker-compose down -v
docker-compose up -d
```

## Production Deployment

### Docker Registry
```bash
# Tag для registry
docker tag bookstore-api:latest your-registry.com/bookstore-api:v1.0.0

# Push в registry
docker push your-registry.com/bookstore-api:v1.0.0
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bookstore-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bookstore-api
  template:
    metadata:
      labels:
        app: bookstore-api
    spec:
      containers:
      - name: api
        image: your-registry.com/bookstore-api:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bookstore-secrets
              key: database-url
```

## Метрики и мониторинг

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2024-01-10T10:00:00Z",
  "version": "1.0.0",
  "service": "bookstore-api",
  "checks": {
    "database": "healthy",
    "memory": "healthy",
    "disk_space": "healthy",
    "environment": "healthy"
  }
}
```

### Prometheus Metrics
- Доступны через `/metrics` endpoint
- Включают метрики приложения и системы
- Интеграция с Grafana для визуализации

## Следующие шаги

1. ✅ **Docker контейнеризация** - завершено
2. 🔄 **Environment Configuration** - в процессе
3. ⏳ **CI/CD Pipeline** - следующий этап
4. ⏳ **Monitoring & Logging** - планируется
5. ⏳ **Cloud Deployment** - финальный этап