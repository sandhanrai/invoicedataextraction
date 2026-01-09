# Invoice AI System - Deployment Guide

## Overview

This guide covers deployment options for the Invoice AI Extraction System, including local development, Docker deployment, and production considerations.

## Prerequisites

### System Requirements

- **OS**: Linux, macOS, or Windows (WSL2 recommended)
- **Python**: 3.8 or higher
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 10GB free space for models and data
- **Docker**: Optional, for containerized deployment

### Dependencies

```bash
# System packages (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev

# Python packages
pip install -r requirements.txt
```

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd invoice-ai-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```bash
# Database
DATABASE_URL=sqlite:///./data/invoice_system.db

# Security
API_KEY=dev-key-12345
SECRET_KEY=your-secret-key-here

# Flask
FLASK_APP=src/ui/flask_app/app.py
FLASK_ENV=development
```

### 3. Initialize Database

```bash
# Create database tables
python -c "from src.db.session import init_db; init_db()"

# Optional: Load sample data
python src/db/ingest_from_json.py --data-dir data/processed --commit
```

### 4. Run Application

```bash
# Start Flask development server
export FLASK_APP=src/ui/flask_app/app.py
flask run

# Or run directly
python src/ui/flask_app/app.py
```

Access the application at: http://localhost:5000

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Build and run
docker-compose -f docker/docker-compose.yml up --build

# Run in background
docker-compose -f docker/docker-compose.yml up -d --build
```

### Manual Docker Build

```bash
# Build image
docker build -f docker/Dockerfile -t invoice-ai-system .

# Run container
docker run -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models/cache:/app/models/cache \
  -e DATABASE_URL=sqlite:///./data/invoice_system.db \
  -e API_KEY=prod-key-secure-123 \
  invoice-ai-system
```

### Docker Environment Variables

```yaml
environment:
  - DATABASE_URL=sqlite:///./data/invoice_system.db # or postgresql://...
  - API_KEY=your-production-api-key
  - SECRET_KEY=your-flask-secret-key
  - FLASK_ENV=production
```

## Production Deployment

### 1. Database Setup

#### SQLite (Simple)

```bash
# SQLite is file-based, no additional setup needed
export DATABASE_URL=sqlite:///./data/invoice_system.db
```

#### PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE invoice_system;
CREATE USER invoice_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE invoice_system TO invoice_user;
\q

# Update environment
export DATABASE_URL=postgresql://invoice_user:secure_password@localhost/invoice_system
```

### 2. Web Server Setup (Gunicorn)

#### Install Gunicorn

```bash
pip install gunicorn
```

#### Create systemd service

```bash
sudo nano /etc/systemd/system/invoice-ai.service
```

```ini
[Unit]
Description=Invoice AI System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/invoice-ai-system
Environment="PATH=/path/to/venv/bin"
Environment="DATABASE_URL=postgresql://invoice_user:secure_password@localhost/invoice_system"
Environment="API_KEY=your-production-api-key"
Environment="SECRET_KEY=your-production-secret"
Environment="FLASK_ENV=production"
ExecStart=/path/to/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 src.ui.flask_app.app:app

[Install]
WantedBy=multi-user.target
```

#### Enable and start service

```bash
sudo systemctl daemon-reload
sudo systemctl enable invoice-ai
sudo systemctl start invoice-ai
sudo systemctl status invoice-ai
```

### 3. Nginx Reverse Proxy (Optional)

#### Install Nginx

```bash
sudo apt-get install nginx
```

#### Create Nginx configuration

```bash
sudo nano /etc/nginx/sites-available/invoice-ai
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /path/to/invoice-ai-system/src/ui/flask_app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Enable site

```bash
sudo ln -s /etc/nginx/sites-available/invoice-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. SSL Certificate (Let's Encrypt)

#### Install Certbot

```bash
sudo apt-get install certbot python3-certbot-nginx
```

#### Get SSL certificate

```bash
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Maintenance

### Health Checks

```bash
# Application health
curl http://localhost:5000/health

# API health with key
curl -H "X-API-KEY: your-key" http://localhost:5000/api/metrics/kpis
```

### Log Management

```bash
# View application logs
sudo journalctl -u invoice-ai -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backup Strategy

#### Database Backup

```bash
# SQLite
cp data/invoice_system.db data/backup_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL
pg_dump invoice_system > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### File Backup

```bash
# Backup uploaded files and processed data
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ models/cache/
```

### Performance Optimization

#### Database Tuning

```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
```

#### Application Scaling

```bash
# Increase Gunicorn workers
gunicorn --workers 8 --bind 0.0.0.0:5000 src.ui.flask_app.app:app

# Use gevent for async workers
pip install gevent
gunicorn --worker-class gevent --workers 4 --bind 0.0.0.0:5000 src.ui.flask_app.app:app
```

## Troubleshooting

### Common Issues

#### Model Loading Errors

```bash
# Clear model cache
rm -rf models/cache/*
# Restart application
sudo systemctl restart invoice-ai
```

#### Database Connection Issues

```bash
# Test database connection
python -c "from src.db.session import SessionLocal; db = SessionLocal(); db.execute('SELECT 1'); print('DB OK')"
```

#### Memory Issues

```bash
# Monitor memory usage
htop
# Check application logs for memory errors
sudo journalctl -u invoice-ai --since "1 hour ago"
```

#### Permission Issues

```bash
# Fix file permissions
sudo chown -R www-data:www-data /path/to/invoice-ai-system
sudo chmod -R 755 /path/to/invoice-ai-system
```

### Debug Mode

```bash
# Run in debug mode for troubleshooting
export FLASK_ENV=development
python src/ui/flask_app/app.py
```

## Security Checklist

- [ ] Change default API keys
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Configure firewall (ufw/iptables)
- [ ] Regular security updates
- [ ] Monitor for suspicious activity
- [ ] Implement rate limiting if needed
- [ ] Regular backup verification

## Update Procedure

### Application Updates

```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run database migrations if needed
python -c "from src.db.session import init_db; init_db()"

# Restart service
sudo systemctl restart invoice-ai
```

### Rolling Updates with Zero Downtime

```bash
# Use blue-green deployment or load balancer
# Update nginx upstream servers
# Gradually shift traffic to new version
# Verify health checks
# Remove old version
```

## Support

For issues and questions:

1. Check application logs: `sudo journalctl -u invoice-ai`
2. Verify system resources: `df -h`, `free -h`
3. Test API endpoints manually
4. Check GitHub issues for known problems
5. Contact development team with detailed error logs
