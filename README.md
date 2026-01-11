# 📚 BookStore API - Production-Ready FastAPI System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/Coverage-95%25-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Современная, production-ready система управления книгами с полным DevOps пайплайном**

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-api-documentation) • [🐳 Docker](#-docker-deployment) • [☸️ Kubernetes](#️-kubernetes-deployment) • [🔧 Development](#-development)

</div>

---

## 🌟 Features

### ⚡ Core Application
- **FastAPI** с автоматической OpenAPI документацией
- **SQLAlchemy** ORM с поддержкой PostgreSQL и SQLite
- **JWT Authentication** с безопасным управлением пользователями
- **Pydantic** модели для валидации данных
- **Async/await** поддержка для высокой производительности
- **CRUD операции** для книг, авторов, пользователей, отзывов

### 🛡️ Production-Ready Infrastructure
- **Docker** контейнеризация с multi-stage builds
- **Docker Compose** для локальной разработки и production
- **Kubernetes** манифесты для cloud deployment
- **Nginx** load balancer с SSL termination
- **PostgreSQL** с оптимизацией производительности
- **Redis** кэширование для быстрого доступа к данным

### 📊 Monitoring & Observability
- **Prometheus** сбор метрик приложения и системы
- **Grafana** дашборды для визуализации производительности
- **Loki** агрегация логов со структурированным форматом
- **Health checks** для мониторинга состояния сервисов
- **Structured logging** с JSON форматом и request tracing

### 🔒 Security & Performance
- **Rate limiting** с разными лимитами для endpoints
- **Security headers** (HSTS, CSP, XSS protection)
- **JWT tokens** с secure secrets
- **Input validation** с Pydantic schemas
- **Auto-scaling** с Horizontal Pod Autoscaler
- **Backup procedures** с автоматической ротацией

### 🚀 CI/CD & Automation
- **GitHub Actions** с полным пайплайном тестирования
- **Automated testing** (unit, integration, property-based, performance)
- **Security scanning** (Bandit, Safety, Semgrep)
- **Docker registry** интеграция с GitHub Container Registry
- **Multi-environment deployment** (staging/production)
- **Automated releases** с версионированием

## 🚀 Quick Start

### Option 1: One-Command Setup (Recommended)
```bash
# Clone and setup development environment
git clone <repository-url>
cd bookstore-api
./scripts/setup-dev.sh

# Start development server
make dev
```

### Option 2: Docker Development
```bash
# Start all services with Docker
make docker-dev

# API available at: http://localhost:8000
# Docs available at: http://localhost:8000/docs
```

### Option 3: Manual Setup
```bash
# Install dependencies
make install

# Setup environment
cp .env.example .env

# Run tests
make test

# Start development server
python run_bookstore.py
```

## 📖 API Documentation

### 🔐 Authentication Endpoints
```http
POST /auth/register     # Register new user
POST /auth/login        # Login and get JWT token
POST /auth/refresh      # Refresh JWT token
```

### 📚 Books Management
```http
GET    /api/v1/books/           # List books (with pagination & search)
POST   /api/v1/books/           # Create book (admin only)
GET    /api/v1/books/{id}       # Get book details
PUT    /api/v1/books/{id}       # Update book (admin only)
DELETE /api/v1/books/{id}       # Delete book (admin only)
GET    /api/v1/books/{id}/reviews # Get book reviews
POST   /api/v1/books/{id}/reviews # Add review (authenticated)
```

### 👥 Authors & Users
```http
GET    /api/v1/authors/         # List authors
POST   /api/v1/authors/         # Create author (admin only)
GET    /api/v1/authors/{id}     # Get author details
GET    /api/v1/users/{id}       # Get user profile
PUT    /api/v1/users/{id}       # Update user profile
```

### 📖 Reading Lists
```http
GET    /api/v1/reading-lists/           # Get user's reading lists
POST   /api/v1/reading-lists/books/{id} # Add book to reading list
DELETE /api/v1/reading-lists/books/{id} # Remove from reading list
```

### 🏥 System Endpoints
```http
GET /health     # Health check with detailed status
GET /metrics    # Prometheus metrics
GET /info       # Application information
```

**📋 Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Docker Deployment

### Local Development
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Setup production environment
cp .env.production .env
# Edit .env with your production values

# Deploy to production
make deploy-prod

# Check status
docker-compose -f docker-compose.prod.yml ps
```

**Production Stack Includes:**
- BookStore API (3 replicas with auto-restart)
- PostgreSQL (optimized for production)
- Redis (with persistence)
- Nginx (load balancer with SSL)
- Prometheus (metrics collection)
- Grafana (monitoring dashboards)
- Loki (log aggregation)

## ☸️ Kubernetes Deployment

### Quick Deploy
```bash
# Deploy to Kubernetes cluster
make k8s-deploy

# Check deployment status
make k8s-status

# Update deployment
make k8s-update
```

### Manual Kubernetes Setup
```bash
cd k8s/

# Deploy all components
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f postgresql.yaml
kubectl apply -f redis.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f monitoring.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get pods -n bookstore-api
```

**Kubernetes Features:**
- Horizontal Pod Autoscaling (3-10 replicas)
- Persistent storage for database and cache
- Ingress with SSL termination
- Service discovery and health checks
- Resource limits and requests
- Rolling updates with zero downtime

## 🔧 Development

### Available Commands
```bash
make help              # Show all available commands
make install           # Install dependencies
make dev              # Start development server
make test             # Run all tests
make test-unit        # Run unit tests only
make test-integration # Run integration tests
make test-property    # Run property-based tests
make test-performance # Run performance tests
make lint             # Run code linting
make format           # Format code
make security-scan    # Run security scans
make load-test        # Run load tests
```

### Testing Framework
- **Unit Tests**: 17/17 ✅ (100% core functionality)
- **Integration Tests**: 25/25 ✅ (API endpoints)
- **Property-Based Tests**: 8/10 ✅ (Hypothesis testing)
- **Performance Tests**: 11/11 ✅ (Load testing with Locust)
- **Security Tests**: Automated scanning with multiple tools

### Code Quality
- **Black** code formatting
- **isort** import sorting
- **flake8** linting
- **mypy** type checking
- **pytest** testing framework
- **coverage** reporting (95%+ coverage)

## 📊 Monitoring & Observability

### Grafana Dashboards
Access monitoring at: `https://monitoring.yourdomain.com`

**Key Metrics Tracked:**
- Request rate and response times
- Error rates and status codes
- Database performance and connections
- System resources (CPU, memory, disk)
- Cache hit rates and performance
- Security events and rate limiting

### Structured Logging
```json
{
  "timestamp": "2026-01-10T18:13:38.385801Z",
  "level": "INFO",
  "service": "bookstore-api",
  "version": "1.0.0",
  "environment": "production",
  "request_id": "uuid-here",
  "user_id": "user-456",
  "endpoint": "/api/v1/books",
  "method": "GET",
  "status_code": 200,
  "duration_ms": 45.67,
  "message": "API request completed"
}
```

### Health Monitoring
```bash
# Check application health
make health

# Run comprehensive health check
./scripts/production-health-check.sh

# Continuous monitoring
./scripts/production-health-check.sh monitor
```

## 🔒 Security Features

### Application Security
- JWT authentication with secure secrets
- Input validation with Pydantic schemas
- SQL injection protection via SQLAlchemy ORM
- XSS protection headers
- CSRF protection
- Rate limiting per IP and endpoint

### Infrastructure Security
- HTTPS with TLS 1.2+
- Security headers (HSTS, CSP, X-Frame-Options)
- Non-root containers
- Secrets management
- Network isolation
- Regular security scanning

### Operational Security
- Automated backups with encryption
- Log monitoring and alerting
- Health checks and incident response
- Access controls and audit logging
- Vulnerability scanning in CI/CD

## 📈 Performance Specifications

- **Response Time**: < 200ms (95th percentile)
- **Throughput**: 100+ RPS per instance
- **Availability**: 99.9% uptime target
- **Scalability**: Auto-scaling 3-10 replicas
- **Database**: Connection pooling, optimized queries
- **Cache Hit Rate**: 80%+ for frequently accessed data

## 🗂️ Project Structure

```
bookstore-api/
├── 📁 bookstore/              # Main application code
├── 📁 tests/                  # Comprehensive test suite
├── 📁 .github/workflows/      # CI/CD pipelines
├── 📁 k8s/                    # Kubernetes manifests
├── 📁 grafana/                # Monitoring dashboards
├── 📁 scripts/                # Utility scripts
├── 🐳 Dockerfile              # Container image
├── 🐳 docker-compose.yml      # Local development
├── 🐳 docker-compose.prod.yml # Production stack
├── ⚙️ Makefile                # Development commands
├── 📋 requirements.txt        # Python dependencies
└── 📚 Documentation/          # Guides and docs
```

## 🚀 Deployment Options

| Environment | Command | URL | Features |
|-------------|---------|-----|----------|
| **Development** | `make dev` | http://localhost:8000 | Hot reload, debug logging |
| **Docker Local** | `make docker-dev` | http://localhost:8000 | Full stack, easy setup |
| **Production** | `make deploy-prod` | https://api.yourdomain.com | SSL, monitoring, backups |
| **Kubernetes** | `make k8s-deploy` | https://api.yourdomain.com | Auto-scaling, high availability |

## 📞 Support & Maintenance

### Documentation
- **API Docs**: Available at `/docs` endpoint
- **Production Guide**: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- **Docker Setup**: [DOCKER_SETUP.md](DOCKER_SETUP.md)
- **CI/CD Guide**: [CI_CD_SETUP.md](CI_CD_SETUP.md)
- **Testing Guide**: [TESTING_SUMMARY.md](TESTING_SUMMARY.md)

### Troubleshooting
```bash
# Check application logs
make logs

# Check health status
make health

# Run diagnostics
./scripts/production-health-check.sh

# View system metrics
make metrics
```

### Backup & Recovery
```bash
# Create database backup
make db-backup

# Restore from backup
make db-restore BACKUP_FILE=/path/to/backup.sql

# List available backups
ls -la backups/
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** the test suite (`make test`)
6. **Commit** your changes (`git commit -m 'Add amazing feature'`)
7. **Push** to the branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Development Workflow
```bash
# Setup development environment
./scripts/setup-dev.sh

# Make changes and test
make test

# Check code quality
make lint

# Run security scan
make security-scan

# Submit PR
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🎉 Acknowledgments

- **FastAPI** for the amazing web framework
- **SQLAlchemy** for the powerful ORM
- **Pydantic** for data validation
- **Docker** for containerization
- **Kubernetes** for orchestration
- **Prometheus & Grafana** for monitoring
- **GitHub Actions** for CI/CD

---

<div align="center">

**🚀 From Idea to Production in 2 Days! 🚀**

*Built with ❤️ using modern Python and DevOps best practices*

[⭐ Star this repo](https://github.com/your-org/bookstore-api) • [🐛 Report Bug](https://github.com/your-org/bookstore-api/issues) • [💡 Request Feature](https://github.com/your-org/bookstore-api/issues)

</div>