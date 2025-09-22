# Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Booking System to production environments. The system supports multiple deployment strategies including Docker, cloud platforms, and traditional server setups.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [Traditional Server Deployment](#traditional-server-deployment)
6. [Database Setup](#database-setup)
7. [SSL/HTTPS Configuration](#sslhttps-configuration)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Backup and Recovery](#backup-and-recovery)
10. [Security Configuration](#security-configuration)
11. [Performance Optimization](#performance-optimization)
12. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+

**Recommended Requirements:**
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **OS**: Ubuntu 22.04 LTS

### Software Dependencies

- **Python**: 3.10+
- **PostgreSQL**: 15+
- **Redis**: 6.0+ (optional, for caching)
- **Nginx**: 1.18+ (optional, for reverse proxy)
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+

## Environment Setup

### Production Environment Variables

Create a `.env.production` file with the following variables:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip-address

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/booking_system_prod

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# OAuth Configuration
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY

# Static Files
STATIC_URL=/static/
STATIC_ROOT=/var/www/booking-system/static/
MEDIA_URL=/media/
MEDIA_ROOT=/var/www/booking-system/media/

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/booking-system/django.log

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Celery (Optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Environment-Specific Settings

Create separate settings files for different environments:

**settings/production.py:**
```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'booking_system_prod',
        'USER': 'booking_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files
STATIC_ROOT = '/var/www/booking-system/static/'
MEDIA_ROOT = '/var/www/booking-system/media/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/booking-system/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Docker Deployment

### Docker Compose Production Setup

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn booking_system.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - static_volume:/var/www/booking-system/static
      - media_volume:/var/www/booking-system/media
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://booking_user:secure_password@db:5432/booking_system_prod
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=booking_system_prod
      - POSTGRES_USER=booking_user
      - POSTGRES_PASSWORD=secure_password
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/var/www/booking-system/static
      - media_volume:/var/www/booking-system/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Production Dockerfile

**Dockerfile.prod:**
```dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories
RUN mkdir -p /var/www/booking-system/static
RUN mkdir -p /var/www/booking-system/media
RUN mkdir -p /var/log/booking-system

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /var/www/booking-system
RUN chown -R appuser:appuser /var/log/booking-system
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "booking_system.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### Deployment Commands

```bash
# Build and start production containers
docker-compose -f docker-compose.prod.yml up -d --build

# Run database migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop containers
docker-compose -f docker-compose.prod.yml down
```

## Cloud Platform Deployment

### AWS Deployment

#### AWS Elastic Beanstalk

1. **Install EB CLI:**
```bash
pip install awsebcli
```

2. **Initialize EB:**
```bash
eb init booking-system
eb create production
```

3. **Configure environment:**
```bash
# .ebextensions/django.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: booking_system.wsgi:application
  aws:elasticbeanstalk:environment:variables:
    DJANGO_SETTINGS_MODULE: booking_system.settings.production
```

4. **Deploy:**
```bash
eb deploy
```

#### AWS ECS with Fargate

**task-definition.json:**
```json
{
  "family": "booking-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "booking-system",
      "image": "your-account.dkr.ecr.region.amazonaws.com/booking-system:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "False"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:booking-system/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/booking-system",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Google Cloud Run

1. **Build and push image:**
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/booking-system
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy booking-system \
  --image gcr.io/PROJECT-ID/booking-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Google App Engine

**app.yaml:**
```yaml
runtime: python310

env_variables:
  DJANGO_SETTINGS_MODULE: booking_system.settings.production
  DEBUG: False

handlers:
- url: /static
  static_dir: static/
- url: /media
  static_dir: media/
- url: /.*
  script: auto
```

### Heroku Deployment

1. **Install Heroku CLI**

2. **Create Heroku app:**
```bash
heroku create your-app-name
```

3. **Configure environment:**
```bash
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgresql://...
```

4. **Deploy:**
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

**Procfile:**
```
web: gunicorn booking_system.wsgi:application --bind 0.0.0.0:$PORT
```

## Traditional Server Deployment

### Ubuntu/Debian Setup

1. **Update system:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install dependencies:**
```bash
sudo apt install -y python3.10 python3.10-venv python3-pip postgresql postgresql-contrib nginx redis-server
```

3. **Create application user:**
```bash
sudo adduser --system --group --shell /bin/bash booking
sudo mkdir -p /var/www/booking-system
sudo chown booking:booking /var/www/booking-system
```

4. **Clone repository:**
```bash
cd /var/www/booking-system
sudo -u booking git clone https://github.com/your-repo/booking-system.git .
```

5. **Setup virtual environment:**
```bash
sudo -u booking python3.10 -m venv venv
sudo -u booking source venv/bin/activate
sudo -u booking pip install -r requirements.txt
```

6. **Configure database:**
```bash
sudo -u postgres createdb booking_system_prod
sudo -u postgres createuser booking_user
sudo -u postgres psql -c "ALTER USER booking_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE booking_system_prod TO booking_user;"
```

7. **Run migrations:**
```bash
sudo -u booking source venv/bin/activate
sudo -u booking python manage.py migrate
sudo -u booking python manage.py collectstatic --noinput
```

### Systemd Service

**/etc/systemd/system/booking-system.service:**
```ini
[Unit]
Description=Booking System Django Application
After=network.target

[Service]
Type=notify
User=booking
Group=booking
WorkingDirectory=/var/www/booking-system
Environment=PATH=/var/www/booking-system/venv/bin
ExecStart=/var/www/booking-system/venv/bin/gunicorn booking_system.wsgi:application --bind 127.0.0.1:8000 --workers 3
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable booking-system
sudo systemctl start booking-system
```

## Database Setup

### PostgreSQL Configuration

**postgresql.conf optimizations:**
```conf
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100
listen_addresses = 'localhost'

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'mod'
log_min_duration_statement = 1000

# Performance
random_page_cost = 1.1
effective_io_concurrency = 200
```

**pg_hba.conf:**
```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

### Database Backup

**Backup script:**
```bash
#!/bin/bash
# /usr/local/bin/backup-booking-system.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/booking-system"
DB_NAME="booking_system_prod"

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U booking_user $DB_NAME | gzip > $BACKUP_DIR/booking_system_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "booking_system_*.sql.gz" -mtime +7 -delete
```

**Cron job:**
```bash
# Add to crontab
0 2 * * * /usr/local/bin/backup-booking-system.sh
```

## SSL/HTTPS Configuration

### Let's Encrypt with Certbot

1. **Install Certbot:**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Obtain certificate:**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

3. **Auto-renewal:**
```bash
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx Configuration

**/etc/nginx/sites-available/booking-system:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/booking-system/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/booking-system/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

## Monitoring and Logging

### Application Monitoring

**Logging configuration:**
```python
# settings/production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/booking-system/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/booking-system/error.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'booking_system': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### System Monitoring

**Install monitoring tools:**
```bash
# Install htop, iotop, nethogs
sudo apt install htop iotop nethogs

# Install Prometheus and Grafana (optional)
# Follow official documentation for setup
```

### Health Checks

**Health check endpoint:**
```python
# views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

def health_check(request):
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check cache (if using Redis)
        cache.set('health_check', 'ok', 10)
        cache_status = cache.get('health_check') == 'ok'
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok' if cache_status else 'error',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
```

## Backup and Recovery

### Automated Backup Script

**backup.sh:**
```bash
#!/bin/bash
set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/booking-system"
DB_NAME="booking_system_prod"
APP_DIR="/var/www/booking-system"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "Backing up database..."
pg_dump -h localhost -U booking_user $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Application files backup
echo "Backing up application files..."
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C $APP_DIR .

# Media files backup
echo "Backing up media files..."
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $APP_DIR media/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Recovery Procedures

**Database recovery:**
```bash
# Stop application
sudo systemctl stop booking-system

# Restore database
gunzip -c /var/backups/booking-system/db_20240115_120000.sql.gz | psql -h localhost -U booking_user booking_system_prod

# Start application
sudo systemctl start booking-system
```

**Application recovery:**
```bash
# Stop application
sudo systemctl stop booking-system

# Restore application files
tar -xzf /var/backups/booking-system/app_20240115_120000.tar.gz -C /var/www/booking-system/

# Run migrations
cd /var/www/booking-system
source venv/bin/activate
python manage.py migrate

# Start application
sudo systemctl start booking-system
```

## Security Configuration

### Firewall Setup

**UFW configuration:**
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow PostgreSQL (if needed)
sudo ufw allow 5432

# Check status
sudo ufw status
```

### Security Headers

**Django security settings:**
```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'

# CSRF settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

### Database Security

**PostgreSQL security:**
```sql
-- Create read-only user for backups
CREATE USER backup_user WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE booking_system_prod TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;

-- Set up row-level security (if needed)
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
CREATE POLICY patient_appointments ON appointments
    FOR ALL TO booking_user
    USING (patient_id = current_setting('app.current_user_id')::integer);
```

## Performance Optimization

### Database Optimization

**PostgreSQL tuning:**
```conf
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
random_page_cost = 1.1
effective_io_concurrency = 200

# Connection pooling
max_connections = 100
```

**Django database optimization:**
```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'booking_system_prod',
        'USER': 'booking_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'OPTIONS': {
                'MAX_CONNS': 20,
            }
        }
    }
}
```

### Caching Configuration

**Redis caching:**
```python
# settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Static Files Optimization

**Nginx static files configuration:**
```nginx
location /static/ {
    alias /var/www/booking-system/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    gzip_static on;
}

location /media/ {
    alias /var/www/booking-system/media/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    gzip_static on;
}
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

**Symptoms**: Database connection errors
**Solutions**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U booking_user -d booking_system_prod

# Check connection limits
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

#### 2. Static Files Not Loading

**Symptoms**: CSS/JS files return 404
**Solutions**:
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check file permissions
ls -la /var/www/booking-system/static/

# Check Nginx configuration
sudo nginx -t
```

#### 3. Memory Issues

**Symptoms**: Out of memory errors
**Solutions**:
```bash
# Check memory usage
free -h
htop

# Optimize Gunicorn workers
# Reduce workers in gunicorn command
gunicorn booking_system.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

#### 4. SSL Certificate Issues

**Symptoms**: SSL errors, mixed content warnings
**Solutions**:
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check Nginx SSL configuration
sudo nginx -t
```

### Log Analysis

**Application logs:**
```bash
# Django logs
tail -f /var/log/booking-system/django.log

# Error logs
tail -f /var/log/booking-system/error.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

**Database logs:**
```bash
# PostgreSQL logs
tail -f /var/log/postgresql/postgresql-*.log
```

### Performance Monitoring

**System monitoring:**
```bash
# CPU and memory usage
htop

# Disk usage
df -h
du -sh /var/www/booking-system/

# Network connections
netstat -tulpn | grep :8000

# Database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### Emergency Procedures

#### 1. Application Down

```bash
# Check service status
sudo systemctl status booking-system

# Restart service
sudo systemctl restart booking-system

# Check logs
sudo journalctl -u booking-system -f
```

#### 2. Database Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check database connectivity
psql -h localhost -U booking_user -d booking_system_prod
```

#### 3. High Load

```bash
# Check system load
uptime
htop

# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Restart services
sudo systemctl restart booking-system
sudo systemctl restart nginx
```

## Maintenance Procedures

### Regular Maintenance Tasks

**Daily:**
- Monitor application logs
- Check disk space
- Verify backup completion

**Weekly:**
- Review error logs
- Check system performance
- Update security patches

**Monthly:**
- Review and rotate logs
- Update dependencies
- Performance analysis

### Update Procedures

**Application updates:**
```bash
# Stop application
sudo systemctl stop booking-system

# Backup current version
cp -r /var/www/booking-system /var/backups/booking-system-$(date +%Y%m%d)

# Update code
cd /var/www/booking-system
sudo -u booking git pull origin main

# Update dependencies
sudo -u booking source venv/bin/activate
sudo -u booking pip install -r requirements.txt

# Run migrations
sudo -u booking python manage.py migrate

# Collect static files
sudo -u booking python manage.py collectstatic --noinput

# Start application
sudo systemctl start booking-system
```

**System updates:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart services
sudo systemctl restart booking-system
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

This deployment guide provides comprehensive instructions for deploying the Booking System to production environments. Follow the appropriate section based on your deployment strategy and requirements.
