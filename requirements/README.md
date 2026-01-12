# Requirements Management

This directory contains all Python dependencies and requirements files.

## 📁 Files

- `base.txt` - Core application dependencies
- `api.txt` - FastAPI and web-related dependencies  
- `testing.txt` - Testing framework dependencies
- `development.txt` - Development tools and utilities

## 🔄 Updating Dependencies

```bash
# Install all dependencies
pip install -r requirements/base.txt -r requirements/api.txt

# Development setup
pip install -r requirements/development.txt -r requirements/testing.txt

# Update dependencies
pip-compile --upgrade requirements/base.in
pip-compile --upgrade requirements/api.in
```

## 📦 Dependency Groups

- **Base**: Core Python packages (SQLAlchemy, Pydantic, etc.)
- **API**: Web framework dependencies (FastAPI, Uvicorn)
- **Testing**: Test frameworks and tools (pytest, hypothesis)
- **Development**: Development tools (black, flake8, mypy)