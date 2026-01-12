# 🚀 Quick Start Guide

This is a quick reference for getting started with the BookStore API.

## 📖 Full Documentation

For comprehensive documentation, see: [documentation/README.md](documentation/README.md)

## ⚡ 30-Second Setup

```bash
# 1. Clone and enter directory
git clone <repository-url>
cd bookstore-api

# 2. Start with Docker (easiest)
cd deployment/docker
docker-compose up -d

# 3. Open in browser
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 🛠️ Development Setup

```bash
# Install dependencies
pip install -r requirements/base.txt -r requirements/api.txt

# Run migrations
python development/scripts/migrate.py upgrade

# Start development server
python run_bookstore.py
```

## 📚 Key Resources

- **API Documentation**: http://localhost:8000/docs
- **Development Guide**: [documentation/guides/DEVELOPMENT_SETUP.md](documentation/guides/DEVELOPMENT_SETUP.md)
- **Docker Guide**: [documentation/guides/DOCKER_SETUP.md](documentation/guides/DOCKER_SETUP.md)
- **Migration Guide**: [documentation/guides/DATABASE_MIGRATIONS.md](documentation/guides/DATABASE_MIGRATIONS.md)

## 🆘 Need Help?

- Check [documentation/](documentation/) directory
- Review [development/examples/](development/examples/) for code samples
- See [Makefile](Makefile) for available commands