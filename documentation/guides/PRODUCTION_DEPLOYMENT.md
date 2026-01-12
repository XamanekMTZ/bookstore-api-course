# 🚀 Production Deployment Guide - BookStore API

## Overview

Comprehensive guide for deploying BookStore API to production with full DevOps pipeline, monitoring, and security best practices.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB+ (16GB+ recommended)
- **Storage**: 100GB+ SSD
- **Network**: Static IP, domain name configured

### Software Requirements
- Docker 24.0+
- Docker Compose 2.0+
- Git 2.30+
- SSL certificates (Let's Encrypt or commercial)

## 🔧 Pre-Deployment Setup

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/bookstore-api
sudo chown $USER:$USER /opt/bookstore-api
cd /opt/bookstore-api
```

### 2. SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Generate certificates
sudo certbot certonly --standalone -d api.yourdomain.com -d monitoring.yourdomain.com

# Copy certificates to project
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*
```

#### Option B: Custom Certificates
```bash
# Copy your certificates
mkdir -p ssl
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem
chmod 600 ssl/*
```

### 3. Environment Configuration

```bash
# Clone repository
git clone https://github.com/your-org/bookstore-api.git .

# Create production environment file
cp .env.production .env

# Edit configuration (IMPORTANT!)
nano .env
```

**Critical Configuration Items:**
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `JWT_SECRET_KEY`: Generate with `openssl rand -hex 32`
- `POSTGRES_PASSWORD`: Strong database password
- `REDIS_PASSWORD`: Strong Redis password
- `GRAFANA_PASSWORD`: Strong Grafana password
- `ALLOWED_ORIGINS`: Your domain(s)

## 🚀 Deployment Process

### 1. Initial Deployment

```bash
# Create required directories
mkdir -p logs backups

# Create Nginx password file for monitoring
sudo apt install apache2-utils -y
htpasswd -c .htpasswd admin

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# Check services status
docker-compose -f docker-compose.prod.yml ps
```

### 2. Database Initialization

```bash
# Wait for database to be ready
docker-compose -f docker-compose.prod.yml exec db pg_isready -U bookstore_user -d bookstore_prod

# Run database migrations (if using Alembic)
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Create initial admin user (optional)
docker-compose -f docker-compose.prod.yml exec api python -c "
from bookstore.auth import create_user
create_user('admin', 'admin@yourdomain.com', 'secure-admin-password')
"
```

### 3. Verification

```bash
# Check health endpoints
curl -k https://api.yourdomain.com/health
curl -k https://api.yourdomain.com/metrics

# Check logs
docker-compose -f docker-compose.prod.yml logs -f api

# Test API functionality
curl -k https://api.yourdomain.com/api/v1/books/
```

## 📊 Monitoring Setup

### 1. Access Monitoring Dashboard

- **Grafana**: https://monitoring.yourdomain.com
- **Username**: admin
- **Password**: (from GRAFANA_PASSWORD in .env)

### 2. Configure Alerts (Optional)

```bash
# Create alertmanager configuration
cat > alertmanager.yml << EOF
global:
  smtp_smarthost: 'smtp.yourdomain.com:587'
  smtp_from: 'alerts@yourdomain.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@yourdomain.com'
    subject: 'BookStore API Alert'
    body: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
EOF
```

## 🔄 CI/CD Integration

### 1. GitHub Actions Setup

Add these secrets to your GitHub repository:

```bash
# Required secrets:
DOCKER_REGISTRY_TOKEN=ghp_your_github_token
PRODUCTION_HOST=your.server.ip
PRODUCTION_USER=deploy
PRODUCTION_SSH_KEY=your_private_ssh_key
```

### 2. Deployment Webhook (Optional)

```bash
# Create deployment webhook script
cat > deploy-webhook.sh << 'EOF'
#!/bin/bash
cd /opt/bookstore-api
git pull origin main
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --no-deps api
EOF

chmod +x deploy-webhook.sh
```

## 🔒 Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. System Security

```bash
# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Setup fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure automatic security updates
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Docker Security

```bash
# Run Docker daemon with security options
sudo mkdir -p /etc/docker
cat > /etc/docker/daemon.json << EOF
{
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp.json"
}
EOF

sudo systemctl restart docker
```

## 📦 Backup & Recovery

### 1. Automated Backups

```bash
# Setup backup cron job
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * cd /opt/bookstore-api && docker-compose -f docker-compose.prod.yml run --rm backup
```

### 2. Manual Backup

```bash
# Create manual backup
docker-compose -f docker-compose.prod.yml run --rm backup

# List backups
ls -la backups/
```

### 3. Restore from Backup

```bash
# Stop API service
docker-compose -f docker-compose.prod.yml stop api

# Restore database
docker-compose -f docker-compose.prod.yml exec db pg_restore \
  -h localhost -U bookstore_user -d bookstore_prod \
  --clean --if-exists \
  /backups/bookstore_backup_YYYYMMDD_HHMMSS.sql.custom

# Start API service
docker-compose -f docker-compose.prod.yml start api
```

## 🔧 Maintenance

### 1. Log Rotation

```bash
# Configure logrotate
sudo cat > /etc/logrotate.d/bookstore-api << EOF
/opt/bookstore-api/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/bookstore-api/docker-compose.prod.yml restart api
    endscript
}
EOF
```

### 2. Updates

```bash
# Update application
cd /opt/bookstore-api
git pull origin main
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### 3. Health Monitoring

```bash
# Create health check script
cat > health-check.sh << 'EOF'
#!/bin/bash
HEALTH_URL="https://api.yourdomain.com/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")

if [ "$RESPONSE" != "200" ]; then
    echo "Health check failed: HTTP $RESPONSE"
    # Send alert (email, Slack, etc.)
    exit 1
fi

echo "Health check passed"
EOF

chmod +x health-check.sh

# Add to cron for monitoring
crontab -e
# Add: */5 * * * * /opt/bookstore-api/health-check.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.prod.yml logs api
   
   # Check configuration
   docker-compose -f docker-compose.prod.yml config
   ```

2. **Database connection issues**
   ```bash
   # Test database connectivity
   docker-compose -f docker-compose.prod.yml exec db pg_isready
   
   # Check database logs
   docker-compose -f docker-compose.prod.yml logs db
   ```

3. **SSL certificate issues**
   ```bash
   # Test certificate
   openssl x509 -in ssl/cert.pem -text -noout
   
   # Check certificate expiry
   openssl x509 -in ssl/cert.pem -noout -dates
   ```

4. **Performance issues**
   ```bash
   # Check resource usage
   docker stats
   
   # Check system resources
   htop
   df -h
   ```

### Emergency Procedures

1. **Rollback deployment**
   ```bash
   # Rollback to previous image
   docker-compose -f docker-compose.prod.yml down
   docker tag bookstore-api:previous bookstore-api:latest
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Emergency maintenance mode**
   ```bash
   # Enable maintenance page
   docker-compose -f docker-compose.prod.yml stop api
   # Configure Nginx to serve maintenance page
   ```

## 📞 Support

- **Documentation**: [Project Wiki](https://github.com/your-org/bookstore-api/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/bookstore-api/issues)
- **Monitoring**: https://monitoring.yourdomain.com
- **Logs**: `/opt/bookstore-api/logs/`

## 📈 Performance Optimization

### Database Optimization
- Regular VACUUM and ANALYZE
- Connection pooling configuration
- Index optimization based on query patterns

### Application Optimization
- Redis caching for frequently accessed data
- API response compression
- Database query optimization

### Infrastructure Optimization
- Load balancer configuration
- CDN for static assets
- Auto-scaling based on metrics

---

**🎉 Congratulations! Your BookStore API is now running in production with full DevOps pipeline!**