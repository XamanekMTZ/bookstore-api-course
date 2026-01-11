# 🐳 Docker и DevOps - Полное руководство

## 🎯 Что мы изучим

Это руководство покрывает все аспекты современного DevOps на примере нашего BookStore API проекта.

### 📁 DevOps структура

```
bookstore-api/
├── 🐳 Dockerfile                   # Многоэтапная сборка контейнера
├── 🐳 docker-compose.yml           # Локальная разработка
├── 🐳 docker-compose.prod.yml      # Production окружение
├── 📁 k8s/                         # Kubernetes манифесты
├── 📁 .github/workflows/           # CI/CD пайплайны
├── 📁 grafana/                     # Мониторинг дашборды
├── 🔧 nginx.conf                   # Конфигурация веб-сервера
├── 📊 prometheus.yml               # Сбор метрик
└── 📋 Makefile                     # Автоматизация команд
```

## 🐳 Docker контейнеризация

### Многоэтапный Dockerfile

```dockerfile
# Dockerfile
# Этап 1: Базовый образ с зависимостями
FROM python:3.11-slim as base

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt fastapi_requirements.txt ./

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r fastapi_requirements.txt

# Этап 2: Production образ
FROM python:3.11-slim as production

WORKDIR /app

# Создание пользователя без root прав
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Копирование зависимостей из базового образа
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Копирование кода приложения
COPY bookstore/ ./bookstore/
COPY run_bookstore.py ./

# Установка прав доступа
RUN chown -R appuser:appuser /app
USER appuser

# Настройка переменных окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["python", "run_bookstore.py"]
```

### Docker Compose для разработки

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./bookstore.db
      - SECRET_KEY=dev-secret-key
      - ENVIRONMENT=development
    volumes:
      - ./bookstore:/app/bookstore
      - ./tests:/app/tests
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: bookstore_dev
      POSTGRES_USER: bookstore_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

  api:
    build: .
    environment:
      - DATABASE_URL=postgresql://bookstore_user:${POSTGRES_PASSWORD}@db:5432/bookstore_prod
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: bookstore_prod
      POSTGRES_USER: bookstore_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./init-prod.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_prod_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana:/etc/grafana/provisioning
    restart: unless-stopped

volumes:
  postgres_prod_data:
  redis_prod_data:
  grafana_data:
```

## ☸️ Kubernetes развертывание

### Namespace и ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bookstore-api

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: bookstore-config
  namespace: bookstore-api
data:
  ENVIRONMENT: "production"
  DATABASE_HOST: "postgresql"
  REDIS_HOST: "redis"
  LOG_LEVEL: "INFO"
```

### Deployment и Service

```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bookstore-api
  namespace: bookstore-api
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
        image: bookstore-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bookstore-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: bookstore-secrets
              key: secret-key
        envFrom:
        - configMapRef:
            name: bookstore-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: bookstore-api-service
  namespace: bookstore-api
spec:
  selector:
    app: bookstore-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bookstore-api-hpa
  namespace: bookstore-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bookstore-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 🚀 CI/CD пайплайн

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r fastapi_requirements.txt
        pip install -r testing_requirements.txt
    
    - name: Run linting
      run: |
        flake8 bookstore/ tests/
        black --check bookstore/ tests/
        isort --check-only bookstore/ tests/
    
    - name: Run tests
      run: |
        pytest --cov=bookstore --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:test_password@localhost:5432/test_db
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        pip install safety bandit
        safety check -r requirements.txt
        bandit -r bookstore/ -f json -o bandit-report.json

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}:latest
          ghcr.io/${{ github.repository }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production..."
        # Здесь будет код развертывания
```

## 📊 Мониторинг и наблюдаемость

### Prometheus конфигурация

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'bookstore-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana дашборд

```json
{
  "dashboard": {
    "title": "BookStore API Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100"
          }
        ]
      }
    ]
  }
}
```

## 🔧 Автоматизация с Makefile

```makefile
# Makefile
.PHONY: help install test lint format clean dev build deploy-local deploy-prod

help: ## Показать справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	pip install -r requirements.txt
	pip install -r fastapi_requirements.txt
	pip install -r testing_requirements.txt

dev: ## Запустить сервер разработки
	python run_bookstore.py

test: ## Запустить все тесты
	pytest tests/ -v --tb=short

test-coverage: ## Запустить тесты с покрытием
	pytest --cov=bookstore --cov-report=html --cov-report=term-missing

lint: ## Проверить код линтерами
	flake8 bookstore/ tests/
	black --check bookstore/ tests/
	isort --check-only bookstore/ tests/
	mypy bookstore/ --ignore-missing-imports

format: ## Отформатировать код
	black bookstore/ tests/
	isort bookstore/ tests/

security-scan: ## Сканирование безопасности
	safety check -r requirements.txt -r fastapi_requirements.txt
	bandit -r bookstore/ -f json -o security-report.json

docker-build: ## Собрать Docker образ
	docker build -t bookstore-api:latest .

docker-dev: ## Запустить среду разработки в Docker
	docker-compose up -d
	@echo "API доступно по адресу: http://localhost:8000"
	@echo "Документация: http://localhost:8000/docs"

docker-prod: ## Запустить production среду
	docker-compose -f docker-compose.prod.yml up -d

k8s-deploy: ## Развернуть в Kubernetes
	kubectl apply -f k8s/

k8s-delete: ## Удалить из Kubernetes
	kubectl delete -f k8s/

logs: ## Показать логи приложения
	docker-compose logs -f api

health: ## Проверить здоровье приложения
	curl -s http://localhost:8000/health | jq .

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/
```

## 🔒 Безопасность

### Секреты в Kubernetes

```yaml
# k8s/secrets.yaml (шаблон)
apiVersion: v1
kind: Secret
metadata:
  name: bookstore-secrets
  namespace: bookstore-api
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  secret-key: <base64-encoded-secret-key>
  jwt-secret: <base64-encoded-jwt-secret>
```

### Nginx конфигурация с безопасностью

```nginx
# nginx-prod.conf
events {
    worker_connections 1024;
}

http {
    # Базовые настройки
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Безопасность
    server_tokens off;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
    
    upstream api_backend {
        server api:8000;
    }
    
    server {
        listen 80;
        server_name api.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;
        
        # SSL конфигурация
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Auth endpoints (более строгие лимиты)
        location /auth/ {
            limit_req zone=auth burst=10 nodelay;
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            proxy_pass http://api_backend;
            access_log off;
        }
    }
}
```

## 📈 Лучшие практики DevOps

### 1. Контейнеризация
- ✅ Многоэтапные Dockerfile для оптимизации размера
- ✅ Непривилегированные пользователи в контейнерах
- ✅ Минимальные базовые образы (alpine, slim)
- ✅ .dockerignore для исключения ненужных файлов

### 2. Оркестрация
- ✅ Kubernetes для production развертывания
- ✅ Health checks и readiness probes
- ✅ Resource limits и requests
- ✅ Horizontal Pod Autoscaling

### 3. CI/CD
- ✅ Автоматизированное тестирование
- ✅ Сканирование безопасности
- ✅ Сборка и публикация образов
- ✅ Развертывание по веткам

### 4. Мониторинг
- ✅ Сбор метрик с Prometheus
- ✅ Визуализация с Grafana
- ✅ Структурированное логирование
- ✅ Алерты и уведомления

### 5. Безопасность
- ✅ Управление секретами
- ✅ Network policies
- ✅ Rate limiting
- ✅ SSL/TLS шифрование

## 🎉 Заключение

### Что мы изучили

**Docker:**
- ✅ Многоэтапные Dockerfile
- ✅ Docker Compose для разработки и production
- ✅ Оптимизация образов и безопасность

**Kubernetes:**
- ✅ Deployments, Services, ConfigMaps
- ✅ Secrets и управление конфигурацией
- ✅ Auto-scaling и health checks

**CI/CD:**
- ✅ GitHub Actions пайплайны
- ✅ Автоматизированное тестирование
- ✅ Сборка и развертывание образов

**Мониторинг:**
- ✅ Prometheus для сбора метрик
- ✅ Grafana для визуализации
- ✅ Структурированное логирование

**Автоматизация:**
- ✅ Makefile для команд разработки
- ✅ Скрипты развертывания
- ✅ Health check мониторинг

### Следующие шаги

1. **Практика**: Разверните свой проект с Docker
2. **Kubernetes**: Изучите продвинутые возможности K8s
3. **Мониторинг**: Настройте алерты и дашборды
4. **Безопасность**: Внедрите security best practices

**Теперь вы знаете как создавать production-ready системы! 🚀**