# BookStore API - Development & Deployment Makefile

.PHONY: help install test lint format clean dev build deploy-local deploy-prod k8s-deploy backup monitor logs

# Default target
help: ## Show this help message
	@echo "BookStore API - Available Commands:"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development
install: ## Install all dependencies
	pip install -r requirements/base.txt
	pip install -r requirements/api.txt
	pip install -r requirements/testing.txt

dev: ## Start development server
	python run_bookstore.py

test: ## Run all tests
	pytest tests/ -v --tb=short

test-unit: ## Run unit tests only
	pytest tests/test_unit_basic.py -v

test-integration: ## Run integration tests only
	pytest tests/test_api_integration.py -v

test-property: ## Run property-based tests only
	pytest tests/test_property_based.py -v --hypothesis-show-statistics

test-performance: ## Run performance tests only
	pytest tests/test_performance.py -v

test-coverage: ## Run tests with coverage report
	coverage run -m pytest
	coverage report --show-missing
	coverage html

lint: ## Run code linting
	flake8 bookstore/ tests/
	black --check bookstore/ tests/
	isort --check-only bookstore/ tests/
	mypy bookstore/ --ignore-missing-imports

format: ## Format code
	black bookstore/ tests/
	isort bookstore/ tests/

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .hypothesis/

# Docker Development
docker-build: ## Build Docker image
	cd deployment/docker && docker build -t bookstore-api:latest .

docker-dev: ## Start development environment with Docker
	cd deployment/docker && docker-compose up -d
	@echo "API available at: http://localhost:8000"
	@echo "Docs available at: http://localhost:8000/docs"

docker-logs: ## Show Docker logs
	cd deployment/docker && docker-compose logs -f api

docker-stop: ## Stop development environment
	cd deployment/docker && docker-compose down

docker-clean: ## Clean up Docker resources
	cd deployment/docker && docker-compose down -v
	docker system prune -f

# Production Deployment
deploy-prod: ## Deploy to production with Docker Compose
	@echo "🚀 Deploying to production..."
	@if [ ! -f .env ]; then echo "❌ .env file not found. Copy .env.production and configure it."; exit 1; fi
	cd deployment/docker && docker-compose -f docker-compose.prod.yml pull
	cd deployment/docker && docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production deployment completed"
	@echo "API: https://api.yourdomain.com"
	@echo "Monitoring: https://monitoring.yourdomain.com"

deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	cd deployment/docker && ENVIRONMENT=staging docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Staging deployment completed"

# Kubernetes
k8s-deploy: ## Deploy to Kubernetes
	@echo "🚀 Deploying to Kubernetes..."
	cd deployment/k8s && ./deploy.sh
	@echo "✅ Kubernetes deployment completed"

k8s-status: ## Check Kubernetes deployment status
	cd deployment/k8s && ./deploy.sh status

k8s-update: ## Update Kubernetes deployment
	cd deployment/k8s && ./deploy.sh update

k8s-delete: ## Delete Kubernetes deployment
	cd deployment/k8s && ./deploy.sh delete

# Database & Migrations
db-migrate: ## Run database migrations to latest version
	python development/scripts/migrate.py upgrade

db-migrate-info: ## Show current migration status
	@echo "📊 Database Migration Status:"
	@echo "============================"
	python development/scripts/migrate.py status

db-create-migration: ## Create new migration (requires MESSAGE env var)
	@if [ -z "$(MESSAGE)" ]; then echo "❌ MESSAGE environment variable required (e.g., make db-create-migration MESSAGE='Add user table')"; exit 1; fi
	python development/scripts/migrate.py create "$(MESSAGE)" --autogenerate

db-downgrade: ## Downgrade database by one migration
	python development/scripts/migrate.py downgrade

db-downgrade-to: ## Downgrade to specific revision (requires REVISION env var)
	@if [ -z "$(REVISION)" ]; then echo "❌ REVISION environment variable required (e.g., make db-downgrade-to REVISION=abc123)"; exit 1; fi
	python development/scripts/migrate.py downgrade $(REVISION)

db-history: ## Show migration history
	python development/scripts/migrate.py history --verbose

db-current: ## Show current migration version
	python development/scripts/migrate.py status

db-backup: ## Create database backup
	cd deployment/docker && docker-compose -f docker-compose.prod.yml run --rm backup

db-restore: ## Restore database from backup (requires BACKUP_FILE env var)
	@if [ -z "$(BACKUP_FILE)" ]; then echo "❌ BACKUP_FILE environment variable required"; exit 1; fi
	cd deployment/docker && docker-compose -f docker-compose.prod.yml exec db pg_restore -h localhost -U bookstore_user -d bookstore_prod --clean --if-exists $(BACKUP_FILE)

# Monitoring
monitor: ## Open monitoring dashboard
	@echo "📊 Opening monitoring dashboard..."
	@echo "Grafana: https://monitoring.yourdomain.com"
	@echo "Prometheus: https://monitoring.yourdomain.com/prometheus"

logs: ## Show application logs
	cd deployment/docker && docker-compose -f docker-compose.prod.yml logs -f api

logs-nginx: ## Show Nginx logs
	cd deployment/docker && docker-compose -f docker-compose.prod.yml logs -f nginx

logs-db: ## Show database logs
	cd deployment/docker && docker-compose -f docker-compose.prod.yml logs -f db

# Health Checks
health: ## Check application health
	@echo "🏥 Checking application health..."
	@curl -s http://localhost:8000/health | jq . || echo "❌ Health check failed"

health-prod: ## Check production health
	@echo "🏥 Checking production health..."
	@curl -s https://api.yourdomain.com/health | jq . || echo "❌ Production health check failed"

metrics: ## Show application metrics
	@echo "📈 Application metrics:"
	@curl -s http://localhost:8000/metrics | head -20

# Security
security-scan: ## Run security scans
	@echo "🔒 Running security scans..."
	safety check -r requirements/base.txt -r requirements/api.txt
	bandit -r bookstore/ -f json -o security-report.json
	@echo "✅ Security scan completed"

# Performance
load-test: ## Run load test against local environment
	@echo "⚡ Running load test..."
	locust -f tests/locustfile.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=60s --headless

load-test-prod: ## Run load test against production
	@echo "⚡ Running production load test..."
	locust -f tests/locustfile.py --host=https://api.yourdomain.com --users=50 --spawn-rate=5 --run-time=300s --headless

# CI/CD
ci-test: ## Run CI tests locally
	@echo "🔄 Running CI tests locally..."
	make lint
	make test
	make security-scan
	@echo "✅ CI tests completed"

release: ## Create a new release
	@echo "🏷️ Creating new release..."
	@if [ -z "$(VERSION)" ]; then echo "❌ VERSION environment variable required (e.g., make release VERSION=1.0.0)"; exit 1; fi
	git tag -a v$(VERSION) -m "Release version $(VERSION)"
	git push origin v$(VERSION)
	@echo "✅ Release v$(VERSION) created"

# Utilities
shell: ## Open shell in API container
	cd deployment/docker && docker-compose exec api bash

db-shell: ## Open database shell
	cd deployment/docker && docker-compose exec db psql -U bookstore_user -d bookstore_prod

redis-shell: ## Open Redis shell
	cd deployment/docker && docker-compose exec redis redis-cli

update-deps: ## Update Python dependencies
	pip-compile --upgrade requirements/base.in
	pip-compile --upgrade requirements/api.in
	pip-compile --upgrade requirements/testing.in

# Documentation
docs: ## Generate API documentation
	@echo "📚 API Documentation available at:"
	@echo "Local: http://localhost:8000/docs"
	@echo "Production: https://api.yourdomain.com/docs"

docs-build: ## Build documentation site
	@echo "📚 Building documentation..."
	# Add documentation build commands here if needed

# Quick Start
quick-start: ## Quick start for new developers
	@echo "🚀 BookStore API Quick Start"
	@echo "============================"
	@echo "1. Installing dependencies..."
	make install
	@echo "2. Starting development environment..."
	make docker-dev
	@echo "3. Running tests..."
	make test
	@echo ""
	@echo "✅ Setup completed!"
	@echo "📖 API Docs: http://localhost:8000/docs"
	@echo "🔍 Health Check: http://localhost:8000/health"
	@echo ""
	@echo "Next steps:"
	@echo "- Edit code in bookstore/ directory"
	@echo "- Run 'make test' to run tests"
	@echo "- Run 'make logs' to see application logs"
	@echo "- Run 'make help' to see all available commands"

# Production Checklist
prod-checklist: ## Production deployment checklist
	@echo "🔍 Production Deployment Checklist"
	@echo "=================================="
	@echo "□ Environment variables configured (.env file)"
	@echo "□ SSL certificates installed"
	@echo "□ Database credentials secured"
	@echo "□ Monitoring configured"
	@echo "□ Backup procedures tested"
	@echo "□ Security scan passed"
	@echo "□ Load testing completed"
	@echo "□ Health checks working"
	@echo "□ Log aggregation configured"
	@echo "□ Incident response plan ready"
	@echo ""
	@echo "Run 'make deploy-prod' when ready!"

# Environment Info
info: ## Show environment information
	@echo "📋 BookStore API Environment Information"
	@echo "======================================="
	@echo "Python Version: $$(python --version)"
	@echo "Docker Version: $$(docker --version)"
	@echo "Docker Compose Version: $$(docker-compose --version)"
	@echo "Kubectl Version: $$(kubectl version --client --short 2>/dev/null || echo 'Not installed')"
	@echo "Current Directory: $$(pwd)"
	@echo "Git Branch: $$(git branch --show-current 2>/dev/null || echo 'Not a git repository')"
	@echo "Git Commit: $$(git rev-parse --short HEAD 2>/dev/null || echo 'Not a git repository')"
	@echo ""
	@echo "Environment Variables:"
	@echo "ENVIRONMENT: $${ENVIRONMENT:-development}"
	@echo "DATABASE_URL: $${DATABASE_URL:-Not set}"
	@echo "REDIS_URL: $${REDIS_URL:-Not set}"