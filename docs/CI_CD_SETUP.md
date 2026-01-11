# 🚀 CI/CD Setup для BookStore API

## Обзор

Полная автоматизация CI/CD пайплайна с использованием GitHub Actions для тестирования, сборки, security сканирования и развертывания BookStore API.

## Структура Workflows

```
.github/workflows/
├── ci.yml              # Основной CI/CD пайплайн
├── dependencies.yml    # Управление зависимостями
└── performance.yml     # Тестирование производительности
```

## Основной CI/CD Pipeline (ci.yml)

### Этапы пайплайна

1. **Test** - Тестирование и линтинг
2. **Security** - Сканирование безопасности
3. **Build** - Сборка Docker образа
4. **Deploy Staging** - Развертывание в staging
5. **Deploy Production** - Развертывание в production
6. **Notify** - Уведомления о результатах

### Триггеры

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
```

### Этап 1: Тестирование

```yaml
services:
  postgres:
    image: postgres:15
  redis:
    image: redis:7-alpine

steps:
  - Checkout code
  - Set up Python 3.11
  - Install dependencies
  - Run linting (black, isort, flake8, mypy)
  - Run unit tests
  - Run integration tests
  - Run property-based tests
  - Run performance tests
  - Generate coverage report
```

**Инструменты качества кода:**
- **Black**: Форматирование кода
- **isort**: Сортировка импортов
- **flake8**: Линтинг кода
- **mypy**: Проверка типов
- **pytest**: Тестирование
- **coverage**: Покрытие кода

### Этап 2: Security Сканирование

```yaml
steps:
  - safety check (зависимости)
  - bandit (код Python)
  - semgrep (статический анализ)
  - Upload security reports
```

**Security инструменты:**
- **Safety**: Проверка уязвимостей в зависимостях
- **Bandit**: Поиск проблем безопасности в коде
- **Semgrep**: Статический анализ безопасности

### Этап 3: Сборка Docker

```yaml
steps:
  - Multi-platform build (amd64, arm64)
  - Push to GitHub Container Registry
  - Generate SBOM (Software Bill of Materials)
  - Cache optimization
```

**Docker особенности:**
- Multi-stage build для оптимизации
- Multi-platform support
- Layer caching для ускорения
- SBOM для отслеживания компонентов

### Этап 4: Развертывание

#### Staging (автоматическое)
- Триггер: push в `develop` ветку
- Автоматическое развертывание
- Smoke tests
- Уведомления

#### Production (с approval)
- Триггер: push в `main` ветку
- Требует manual approval
- Blue-green deployment
- Health checks
- Создание release

## Управление зависимостями (dependencies.yml)

### Автоматические обновления

```yaml
schedule:
  - cron: '0 9 * * 1'  # Каждый понедельник в 9:00
```

**Функции:**
- Обновление Python зависимостей
- Security сканирование
- Создание Pull Request с обновлениями
- Проверка лицензий

### Инструменты

- **pip-tools**: Управление зависимостями
- **safety**: Проверка уязвимостей
- **Trivy**: Сканирование Docker образов
- **Snyk**: Дополнительное security сканирование

## Performance Testing (performance.yml)

### Нагрузочное тестирование

```yaml
schedule:
  - cron: '0 2 * * *'  # Каждый день в 2:00
```

**Возможности:**
- Load testing с Locust
- Uptime monitoring
- Metrics analysis
- Performance reports

### Locust конфигурация

```python
class BookStoreUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_books(self):
        self.client.get("/api/v1/books/")
    
    @task(2)
    def view_book_details(self):
        book_id = random.randint(1, 10)
        self.client.get(f"/api/v1/books/{book_id}")
```

## Конфигурация проекта

### pyproject.toml

```toml
[tool.black]
line-length = 127
target-version = ['py311']

[tool.isort]
profile = "black"
line-length = 127

[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
```

### .flake8

```ini
[flake8]
max-line-length = 127
max-complexity = 10
ignore = E203,E501,W503
exclude = .git,__pycache__,.venv,build,dist
```

## Environments и Secrets

### GitHub Environments

1. **staging**
   - Автоматическое развертывание
   - Staging URL
   - Тестовые данные

2. **production**
   - Manual approval required
   - Production URL
   - Production secrets

### Required Secrets

```yaml
secrets:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # Автоматически
  SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}      # Для Snyk сканирования
  DOCKER_REGISTRY_TOKEN: ${{ secrets.DOCKER_REGISTRY_TOKEN }}
```

## Мониторинг и Алерты

### Метрики пайплайна

- Build time
- Test success rate
- Security scan results
- Deployment frequency
- Lead time for changes

### Уведомления

- ✅ Успешные deployments
- ❌ Неудачные builds
- ⚠️ Security vulnerabilities
- 📊 Performance degradation

## Качественные гейты

### Обязательные проверки

- ✅ Все тесты должны пройти
- ✅ Coverage > 80%
- ✅ Security scan без критических уязвимостей
- ✅ Linting без ошибок
- ✅ Type checking без ошибок

### Performance критерии

- ⚡ Average response time < 500ms
- 📈 95th percentile < 1000ms
- ❌ Error rate < 1%
- 🔄 Throughput > 100 RPS

## Локальная разработка

### Pre-commit hooks

```bash
# Установка pre-commit
pip install pre-commit
pre-commit install

# Запуск проверок
pre-commit run --all-files
```

### Локальное тестирование

```bash
# Полный набор тестов
make test

# Только unit тесты
make test-unit

# Только integration тесты
make test-integration

# Performance тесты
make test-performance

# Linting
make lint

# Security scan
make security-scan
```

## Troubleshooting

### Частые проблемы

1. **Тесты падают в CI, но проходят локально**
   - Проверить переменные окружения
   - Убедиться в версиях зависимостей
   - Проверить services (postgres, redis)

2. **Docker build fails**
   - Проверить .dockerignore
   - Убедиться в корректности Dockerfile
   - Проверить размер контекста

3. **Security scan находит уязвимости**
   - Обновить зависимости
   - Проверить safety-db
   - Исключить false positives

### Отладка

```bash
# Локальный запуск GitHub Actions
act -j test

# Проверка Docker build
docker build -t bookstore-api:test .

# Локальный security scan
bandit -r bookstore/
safety check
```

## Метрики и KPI

### DevOps метрики

- **Deployment Frequency**: Ежедневно
- **Lead Time**: < 2 часа
- **MTTR**: < 30 минут
- **Change Failure Rate**: < 5%

### Quality метрики

- **Test Coverage**: > 90%
- **Code Quality**: A grade
- **Security Score**: > 95%
- **Performance**: SLA compliance

## Следующие шаги

1. ✅ **CI/CD Pipeline** - реализован
2. 🔄 **Monitoring Integration** - в процессе
3. ⏳ **Advanced Security** - планируется
4. ⏳ **Multi-environment** - планируется

Система CI/CD готова к production использованию! 🚀