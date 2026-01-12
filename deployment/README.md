# Deployment Configuration

This directory contains all deployment-related files and configurations.

## 📁 Structure

- `docker/` - Docker configurations and compose files
- `k8s/` - Kubernetes manifests and deployment scripts
- `config/` - Configuration files for different environments
- `monitoring/` - Monitoring and observability configurations

## 🚀 Quick Deploy

```bash
# Local development
cd deployment/docker && docker-compose up -d

# Production
cd deployment/docker && docker-compose -f docker-compose.prod.yml up -d

# Kubernetes
cd deployment/k8s && ./deploy.sh
```

## 📖 Documentation

See [deployment guides](../documentation/guides/) for detailed instructions.