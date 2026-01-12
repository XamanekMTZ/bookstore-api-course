# 📁 Project Structure Guide

This document explains the organized structure of the BookStore API project.

## 🎯 Why We Reorganized

The project was reorganized to improve:
- **Navigation** - Easier to find what you need
- **Maintenance** - Logical grouping of related files
- **Onboarding** - Clear structure for new developers
- **Deployment** - Separated deployment configs from code

## 📂 Directory Structure

### 🏠 Root Level
```
bookstore-api/
├── 📁 bookstore/          # Core application code
├── 📁 tests/              # All test files
├── 📁 alembic/            # Database migrations
├── 📁 deployment/         # Deployment configurations
├── 📁 development/        # Development tools & examples
├── 📁 documentation/      # All documentation
├── 📁 requirements/       # Python dependencies
├── 📁 archive/            # Archived/legacy files
├── 📁 .github/            # GitHub Actions workflows
├── 📁 .kiro/              # Kiro specifications
├── ⚙️ Makefile            # Development commands
├── 📋 alembic.ini         # Migration configuration
├── 🐍 run_bookstore.py    # Application entry point
├── 📚 README.md           # Main documentation
├── 📚 QUICK_START.md      # Quick start guide
└── 📄 LICENSE             # MIT License
```

### 🚀 deployment/
**Purpose**: All deployment-related configurations
```
deployment/
├── docker/                # Docker configurations
│   ├── Dockerfile         # Container image definition
│   ├── docker-compose.yml # Development environment
│   ├── docker-compose.prod.yml # Production stack
│   └── .dockerignore      # Docker ignore rules
├── k8s/                   # Kubernetes manifests
│   ├── deploy.sh          # Deployment script
│   ├── api-deployment.yaml
│   ├── monitoring.yaml
│   └── ...
├── config/                # Environment configurations
│   ├── nginx.conf         # Nginx configuration
│   ├── prometheus.yml     # Monitoring config
│   └── ...
└── monitoring/            # Monitoring dashboards
    └── grafana/           # Grafana dashboards
```

**Usage**:
```bash
# Docker development
cd deployment/docker && docker-compose up -d

# Kubernetes deployment
cd deployment/k8s && ./deploy.sh

# Production deployment
cd deployment/docker && docker-compose -f docker-compose.prod.yml up -d
```

### 🛠️ development/
**Purpose**: Development tools, scripts, and learning materials
```
development/
├── scripts/               # Utility scripts
│   ├── migrate.py         # Database migration manager
│   ├── setup-dev.sh       # Development setup
│   ├── production-health-check.sh
│   └── ...
├── examples/              # Code examples & tutorials
│   ├── fastapi_cheatsheet.md
│   ├── testing_cheatsheet.md
│   ├── oop_practice.py
│   └── ...
└── tools/                 # Development utilities
    ├── create_data_via_api.py
    ├── create_test_data.py
    └── ...
```

**Usage**:
```bash
# Run migrations
python development/scripts/migrate.py upgrade

# Setup development environment
./development/scripts/setup-dev.sh

# Check examples
ls development/examples/
```

### 📚 documentation/
**Purpose**: Comprehensive project documentation
```
documentation/
├── guides/                # Step-by-step guides
│   ├── QUICK_START.md     # Getting started
│   ├── DATABASE_MIGRATIONS.md # Migration guide
│   ├── DOCKER_SETUP.md    # Docker guide
│   ├── PRODUCTION_DEPLOYMENT.md
│   └── ...
├── api/                   # API documentation
│   └── (future: OpenAPI specs, etc.)
└── project/               # Project documentation
    └── (future: architecture docs, etc.)
```

**Usage**:
- Start with [documentation/README.md](documentation/README.md)
- Follow guides in [documentation/guides/](documentation/guides/)
- Check API docs at http://localhost:8000/docs

### 📦 requirements/
**Purpose**: Organized Python dependencies
```
requirements/
├── base.txt               # Core dependencies (SQLAlchemy, etc.)
├── api.txt                # FastAPI and web dependencies
├── testing.txt            # Testing frameworks
├── base.in                # Source files for pip-compile
├── api.in
└── testing.in
```

**Usage**:
```bash
# Install all dependencies
pip install -r requirements/base.txt -r requirements/api.txt

# Development setup
pip install -r requirements/testing.txt

# Update dependencies
pip-compile --upgrade requirements/base.in
```

### 🗄️ archive/
**Purpose**: Legacy and completed files
```
archive/
├── FINAL_SUMMARY.md       # Project completion summary
├── PROJECT_COMPLETION_SUMMARY.md
├── LEARNING_README.md     # Learning materials
├── social-media-posts.md  # Marketing content
└── localization_backups/  # Localization history
```

## 🔄 Migration from Old Structure

### What Moved Where

| Old Location | New Location | Reason |
|-------------|-------------|---------|
| `Dockerfile` | `deployment/docker/` | Deployment organization |
| `docker-compose.yml` | `deployment/docker/` | Deployment organization |
| `k8s/` | `deployment/k8s/` | Deployment organization |
| `config/` | `deployment/config/` | Deployment organization |
| `grafana/` | `deployment/monitoring/` | Monitoring organization |
| `scripts/` | `development/scripts/` | Development tools |
| `examples/` | `development/examples/` | Learning materials |
| `docs/` | `documentation/guides/` | Documentation organization |
| `requirements.txt` | `requirements/base.txt` | Dependency organization |
| `fastapi_requirements.txt` | `requirements/api.txt` | Dependency organization |
| Legacy files | `archive/` | Cleanup |

### Updated Commands

| Old Command | New Command | Notes |
|------------|------------|-------|
| `docker-compose up` | `cd deployment/docker && docker-compose up` | Path change |
| `alembic upgrade head` | `python development/scripts/migrate.py upgrade` | Enhanced script |
| `pip install -r requirements.txt` | `pip install -r requirements/base.txt -r requirements/api.txt` | Split dependencies |

## 🎯 Benefits of New Structure

### 👥 For Developers
- **Clearer navigation** - Know where to find things
- **Logical grouping** - Related files are together
- **Better onboarding** - Obvious starting points
- **Reduced clutter** - Clean root directory

### 🚀 For Deployment
- **Isolated configs** - Deployment files in one place
- **Environment separation** - Clear dev/prod distinction
- **Docker context** - Proper build context
- **K8s organization** - All manifests together

### 📚 For Documentation
- **Centralized docs** - All guides in one place
- **Progressive disclosure** - Start simple, go deep
- **Cross-references** - Easy linking between docs
- **Maintenance** - Easier to keep updated

## 🔧 Working with New Structure

### Development Workflow
```bash
# 1. Start here
cat README.md

# 2. Quick start
cat QUICK_START.md

# 3. Development setup
./development/scripts/setup-dev.sh

# 4. Run migrations
python development/scripts/migrate.py upgrade

# 5. Start coding
python run_bookstore.py
```

### Deployment Workflow
```bash
# 1. Local testing
cd deployment/docker
docker-compose up -d

# 2. Production deployment
docker-compose -f docker-compose.prod.yml up -d

# 3. Kubernetes (if needed)
cd ../k8s
./deploy.sh
```

### Learning Workflow
```bash
# 1. Read documentation
ls documentation/guides/

# 2. Check examples
ls development/examples/

# 3. Try tools
python development/scripts/migrate.py --help
```

## 🆘 Troubleshooting

### Path Issues
If you get path errors after reorganization:
1. Check if you're in the right directory
2. Update any custom scripts with new paths
3. Use absolute paths in automation

### Missing Files
If you can't find a file:
1. Check the migration table above
2. Look in `archive/` for legacy files
3. Search the entire project: `find . -name "filename"`

### Docker Issues
If Docker builds fail:
1. Update build context: `cd deployment/docker`
2. Check Dockerfile paths are relative to new location
3. Rebuild with `--no-cache` flag

## 📞 Getting Help

- **Structure questions**: Check this document
- **Development help**: See [documentation/guides/](documentation/guides/)
- **Examples**: Browse [development/examples/](development/examples/)
- **Issues**: Create GitHub issue with `structure` label

---

**Remember**: The new structure is designed to scale with the project and make everyone's life easier! 🎉