# Enhanced Kalshi Trading Bot - Deployment Guide

This comprehensive guide covers all aspects of deploying the Enhanced Kalshi Trading Bot in various environments, from local development to production cloud deployments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [Cloud Deployment Options](#cloud-deployment-options)
- [Docker Deployment](#docker-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 10 GB free space
- **Network**: Stable internet connection (minimum 10 Mbps)
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+

#### Recommended Requirements
- **CPU**: 4+ cores, 3.0+ GHz
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: High-speed internet (100+ Mbps)
- **OS**: Linux (Ubuntu 22.04 LTS)

### Software Dependencies

#### Core Dependencies
- **Python**: 3.9 or higher
- **Node.js**: 18.0 or higher
- **npm**: 8.0 or higher
- **Git**: Latest version
- **SQLite**: 3.35 or higher

#### Optional Dependencies
- **Docker**: 20.10 or higher (for containerized deployment)
- **Docker Compose**: 2.0 or higher
- **Redis**: 6.0 or higher (for caching)
- **PostgreSQL**: 13 or higher (for production database)

### API Access Requirements

#### Kalshi API
- Valid Kalshi trading account
- API key and secret
- Sufficient account balance for trading
- Verified account status

#### External APIs (Optional)
- News API key for sentiment analysis
- Twitter API bearer token
- Financial data provider API keys

## Local Development Setup

### Step 1: Environment Preparation

#### Clone Repository
```bash
git clone https://github.com/your-username/enhanced-kalshi-bot.git
cd enhanced-kalshi-bot
```

#### Create Virtual Environment
```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.9+
```

#### Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Install Node.js Dependencies
```bash
# Desktop Admin Panel
cd desktop_admin_panel
npm install
cd ..

# Telegram Web App
cd telegram_webapp
npm install
cd ..
```

### Step 2: Configuration Setup

#### Environment Variables
```bash
# Copy example configuration
cp config/.env.example config/.env

# Edit configuration file
nano config/.env
```

#### Sample Configuration
```env
# Kalshi API Configuration
KALSHI_API_KEY=your_api_key_here
KALSHI_API_SECRET=your_api_secret_here
KALSHI_BASE_URL=https://trading-api.kalshi.com/trade-api/v2
KALSHI_ENVIRONMENT=demo  # Use 'demo' for testing, 'production' for live trading

# Database Configuration
DATABASE_URL=sqlite:///data/trading_bot.db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Trading Configuration
MAX_POSITION_SIZE=0.10
RISK_LEVEL=medium
TRADING_INTERVAL=300
ENABLE_PAPER_TRADING=true

# Sentiment Analysis Configuration
SENTIMENT_MODEL_PATH=models/sentiment/
NEWS_API_KEY=your_news_api_key
TWITTER_BEARER_TOKEN=your_twitter_token
SENTIMENT_UPDATE_INTERVAL=3600

# Risk Management
MAX_DAILY_LOSS=500
MAX_DRAWDOWN=0.20
STOP_LOSS_ENABLED=true
STOP_LOSS_PERCENTAGE=0.15

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/trading_bot.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=5

# UI Configuration
ADMIN_PANEL_PORT=5173
TELEGRAM_WEBAPP_PORT=5174
ENABLE_CORS=true

# Security Configuration
SECRET_KEY=your_secret_key_here
JWT_EXPIRATION=3600
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Step 3: Database Initialization

#### Create Database Schema
```bash
python src/core/database.py
```

#### Verify Database Setup
```bash
sqlite3 data/trading_bot.db ".tables"
```

### Step 4: Model Setup

#### Download Sentiment Models
```bash
python scripts/download_models.py
```

#### Verify Model Installation
```bash
python -c "from src.ml_models.sentiment_analyzer import SentimentAnalyzer; print('Models loaded successfully')"
```

### Step 5: Development Server Startup

#### Start Backend Services
```bash
# Terminal 1: Main trading engine
python src/main.py

# Terminal 2: API server (if separate)
python src/api/server.py
```

#### Start Frontend Services
```bash
# Terminal 3: Desktop admin panel
cd desktop_admin_panel
npm run dev

# Terminal 4: Telegram web app
cd telegram_webapp
npm run dev
```

#### Verify Installation
- Backend API: `http://localhost:8000/health`
- Desktop Admin Panel: `http://localhost:5173`
- Telegram Web App: `http://localhost:5174`

## Production Deployment

### Step 1: Production Environment Setup

#### Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.9 python3.9-venv python3-pip nodejs npm git sqlite3 nginx supervisor

# Create application user
sudo useradd -m -s /bin/bash kalshi-bot
sudo usermod -aG sudo kalshi-bot
```

#### Application Deployment
```bash
# Switch to application user
sudo su - kalshi-bot

# Clone repository
git clone https://github.com/your-username/enhanced-kalshi-bot.git
cd enhanced-kalshi-bot

# Create production virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

### Step 2: Production Configuration

#### Environment Configuration
```bash
# Create production environment file
cp config/.env.example config/.env.production

# Edit with production values
nano config/.env.production
```

#### Production Environment Variables
```env
# Production-specific settings
KALSHI_ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@localhost/kalshi_bot
REDIS_URL=redis://localhost:6379/0

# Security settings
DEBUG=false
SECRET_KEY=your_production_secret_key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Performance settings
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=100

# Monitoring
SENTRY_DSN=your_sentry_dsn
DATADOG_API_KEY=your_datadog_key
```

### Step 3: Database Setup

#### PostgreSQL Installation (Recommended for Production)
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE kalshi_bot;
CREATE USER kalshi_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE kalshi_bot TO kalshi_user;
\q
```

#### Database Migration
```bash
# Run database migrations
python src/core/database.py --migrate

# Verify database setup
python -c "from src.core.database import DatabaseManager; print('Database connected successfully')"
```

### Step 4: Frontend Build

#### Build Production Assets
```bash
# Build desktop admin panel
cd desktop_admin_panel
npm ci --production
npm run build

# Build Telegram web app
cd ../telegram_webapp
npm ci --production
npm run build
```

#### Configure Web Server
```nginx
# /etc/nginx/sites-available/kalshi-bot
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL configuration
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    
    # Desktop admin panel
    location / {
        root /home/kalshi-bot/enhanced-kalshi-bot/desktop_admin_panel/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Telegram web app
    location /telegram/ {
        root /home/kalshi-bot/enhanced-kalshi-bot/telegram_webapp/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Step 5: Process Management

#### Supervisor Configuration
```ini
# /etc/supervisor/conf.d/kalshi-bot.conf
[program:kalshi-bot-api]
command=/home/kalshi-bot/enhanced-kalshi-bot/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 src.api.wsgi:application
directory=/home/kalshi-bot/enhanced-kalshi-bot
user=kalshi-bot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/kalshi-bot/api.log

[program:kalshi-bot-engine]
command=/home/kalshi-bot/enhanced-kalshi-bot/venv/bin/python src/main.py
directory=/home/kalshi-bot/enhanced-kalshi-bot
user=kalshi-bot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/kalshi-bot/engine.log

[program:kalshi-bot-worker]
command=/home/kalshi-bot/enhanced-kalshi-bot/venv/bin/python src/workers/background_worker.py
directory=/home/kalshi-bot/enhanced-kalshi-bot
user=kalshi-bot
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/kalshi-bot/worker.log
```

#### Start Services
```bash
# Enable and start services
sudo systemctl enable supervisor
sudo systemctl start supervisor

# Reload supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start application processes
sudo supervisorctl start kalshi-bot-api
sudo supervisorctl start kalshi-bot-engine
sudo supervisorctl start kalshi-bot-worker

# Enable and start nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

## Cloud Deployment Options

### AWS Deployment

#### Architecture Overview
- **EC2**: Application servers
- **RDS**: PostgreSQL database
- **ElastiCache**: Redis caching
- **S3**: Static asset storage
- **CloudFront**: CDN for frontend
- **ALB**: Application load balancer
- **Route 53**: DNS management

#### Infrastructure as Code (Terraform)
```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# VPC and networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "kalshi-bot-vpc"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "kalshi-bot-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = aws_subnet.public[*].id
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier     = "kalshi-bot-db"
  engine         = "postgres"
  engine_version = "13.7"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "kalshi_bot"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "kalshi-bot-final-snapshot"
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "kalshi-bot-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "kalshi-bot-cache"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.elasticache.id]
}

# EC2 instances
resource "aws_launch_template" "main" {
  name_prefix   = "kalshi-bot-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  
  vpc_security_group_ids = [aws_security_group.ec2.id]
  
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    db_host     = aws_db_instance.main.endpoint
    redis_host  = aws_elasticache_cluster.main.cache_nodes[0].address
  }))
  
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "kalshi-bot-instance"
    }
  }
}

resource "aws_autoscaling_group" "main" {
  name                = "kalshi-bot-asg"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.main.arn]
  health_check_type   = "ELB"
  
  min_size         = 1
  max_size         = 3
  desired_capacity = 2
  
  launch_template {
    id      = aws_launch_template.main.id
    version = "$Latest"
  }
}
```

#### Deployment Script
```bash
#!/bin/bash
# deploy-aws.sh

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="production.tfvars"

# Apply infrastructure
terraform apply -var-file="production.tfvars" -auto-approve

# Get outputs
ALB_DNS=$(terraform output -raw alb_dns_name)
DB_ENDPOINT=$(terraform output -raw db_endpoint)

echo "Deployment complete!"
echo "Application URL: https://$ALB_DNS"
echo "Database endpoint: $DB_ENDPOINT"
```

### Google Cloud Platform Deployment

#### Cloud Run Deployment
```yaml
# cloudbuild.yaml
steps:
  # Build backend container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/kalshi-bot:$COMMIT_SHA', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/kalshi-bot:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'kalshi-bot'
      - '--image'
      - 'gcr.io/$PROJECT_ID/kalshi-bot:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'

  # Build and deploy frontend
  - name: 'node:18'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd desktop_admin_panel
        npm ci
        npm run build
        gsutil -m rsync -r -d dist gs://$PROJECT_ID-frontend
```

#### Deployment Commands
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sql-component.googleapis.com

# Create Cloud SQL instance
gcloud sql instances create kalshi-bot-db \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create kalshi_bot --instance=kalshi-bot-db

# Deploy application
gcloud builds submit --config cloudbuild.yaml
```

### Azure Deployment

#### Container Instances Deployment
```yaml
# azure-deploy.yml
apiVersion: 2019-12-01
location: eastus
name: kalshi-bot-container-group
properties:
  containers:
  - name: kalshi-bot-api
    properties:
      image: your-registry.azurecr.io/kalshi-bot:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 2
      ports:
      - port: 8000
      environmentVariables:
      - name: DATABASE_URL
        secureValue: postgresql://user:pass@server/db
      - name: REDIS_URL
        secureValue: redis://cache:6379/0
  
  - name: kalshi-bot-worker
    properties:
      image: your-registry.azurecr.io/kalshi-bot:latest
      command: ["python", "src/workers/background_worker.py"]
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 1
      environmentVariables:
      - name: DATABASE_URL
        secureValue: postgresql://user:pass@server/db
  
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 8000
  restartPolicy: Always
```

#### Deployment Script
```bash
#!/bin/bash
# deploy-azure.sh

# Create resource group
az group create --name kalshi-bot-rg --location eastus

# Create container registry
az acr create --resource-group kalshi-bot-rg --name kalshiBotRegistry --sku Basic

# Build and push image
az acr build --registry kalshiBotRegistry --image kalshi-bot:latest .

# Create PostgreSQL server
az postgres server create \
    --resource-group kalshi-bot-rg \
    --name kalshi-bot-db \
    --location eastus \
    --admin-user kalshi_admin \
    --admin-password SecurePassword123! \
    --sku-name B_Gen5_1

# Deploy container group
az container create --resource-group kalshi-bot-rg --file azure-deploy.yml
```

## Docker Deployment

### Docker Configuration

#### Main Application Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "src/main.py"]
```

#### Frontend Dockerfile
```dockerfile
# desktop_admin_panel/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: kalshi_bot
      POSTGRES_USER: kalshi_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U kalshi_user -d kalshi_bot"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Main Application
  kalshi-bot:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DATABASE_URL=postgresql://kalshi_user:secure_password@postgres:5432/kalshi_bot
      - REDIS_URL=redis://redis:6379/0
      - KALSHI_API_KEY=${KALSHI_API_KEY}
      - KALSHI_API_SECRET=${KALSHI_API_SECRET}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Background Worker
  worker:
    build: .
    command: ["python", "src/workers/background_worker.py"]
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://kalshi_user:secure_password@postgres:5432/kalshi_bot
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Desktop Admin Panel
  admin-panel:
    build: ./desktop_admin_panel
    ports:
      - "80:80"
    depends_on:
      - kalshi-bot
    restart: unless-stopped

  # Telegram Web App
  telegram-app:
    build: ./telegram_webapp
    ports:
      - "8080:80"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - kalshi-bot
      - admin-panel
    restart: unless-stopped

  # Application with production settings
  kalshi-bot:
    build: .
    environment:
      - NODE_ENV=production
      - DEBUG=false
      - DATABASE_URL=postgresql://kalshi_user:${DB_PASSWORD}@postgres:5432/kalshi_bot
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - KALSHI_API_KEY=${KALSHI_API_KEY}
      - KALSHI_API_SECRET=${KALSHI_API_SECRET}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  # Production database with backup
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: kalshi_bot
      POSTGRES_USER: kalshi_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G

volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/kalshi-bot/data
```

### Deployment Commands

#### Development Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale worker=3

# Stop services
docker-compose down
```

#### Production Deployment
```bash
# Build and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitor services
docker-compose ps
docker-compose logs -f kalshi-bot

# Update application
docker-compose pull
docker-compose up -d --no-deps kalshi-bot

# Backup database
docker-compose exec postgres pg_dump -U kalshi_user kalshi_bot > backup.sql
```

## Monitoring and Maintenance

### Application Monitoring

#### Health Checks
```python
# src/api/health.py
from flask import Flask, jsonify
from src.core.database import DatabaseManager
from src.api.kalshi_client import KalshiClient

app = Flask(__name__)

@app.route('/health')
def health_check():
    checks = {
        'database': check_database(),
        'kalshi_api': check_kalshi_api(),
        'redis': check_redis(),
        'disk_space': check_disk_space(),
        'memory': check_memory()
    }
    
    status = 'healthy' if all(checks.values()) else 'unhealthy'
    
    return jsonify({
        'status': status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }), 200 if status == 'healthy' else 503

def check_database():
    try:
        db = DatabaseManager()
        db.execute_query("SELECT 1")
        return True
    except Exception:
        return False

def check_kalshi_api():
    try:
        client = KalshiClient()
        client.get_markets(limit=1)
        return True
    except Exception:
        return False
```

#### Logging Configuration
```python
# src/utils/logging_config.py
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                'logs/trading_bot.log',
                maxBytes=100*1024*1024,  # 100MB
                backupCount=5
            ),
            
            # Error file handler
            logging.handlers.RotatingFileHandler(
                'logs/errors.log',
                maxBytes=50*1024*1024,   # 50MB
                backupCount=3
            )
        ]
    )
    
    # Configure specific loggers
    trading_logger = logging.getLogger('trading')
    trading_logger.addHandler(
        logging.handlers.RotatingFileHandler(
            'logs/trading.log',
            maxBytes=50*1024*1024,
            backupCount=10
        )
    )
    
    performance_logger = logging.getLogger('performance')
    performance_logger.addHandler(
        logging.handlers.RotatingFileHandler(
            'logs/performance.log',
            maxBytes=25*1024*1024,
            backupCount=5
        )
    )
```

#### Metrics Collection
```python
# src/monitoring/metrics.py
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
TRADES_TOTAL = Counter('trades_total', 'Total number of trades', ['strategy', 'outcome'])
TRADE_DURATION = Histogram('trade_duration_seconds', 'Time spent processing trades')
PORTFOLIO_VALUE = Gauge('portfolio_value_dollars', 'Current portfolio value')
SYSTEM_CPU = Gauge('system_cpu_percent', 'System CPU usage')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'System memory usage')

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        
    def record_trade(self, strategy, outcome, duration):
        TRADES_TOTAL.labels(strategy=strategy, outcome=outcome).inc()
        TRADE_DURATION.observe(duration)
        
    def update_portfolio_value(self, value):
        PORTFOLIO_VALUE.set(value)
        
    def update_system_metrics(self):
        SYSTEM_CPU.set(psutil.cpu_percent())
        SYSTEM_MEMORY.set(psutil.virtual_memory().percent)
        
    def start_metrics_server(self, port=8001):
        start_http_server(port)
```

### Database Maintenance

#### Backup Strategy
```bash
#!/bin/bash
# scripts/backup_database.sh

BACKUP_DIR="/opt/kalshi-bot/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="kalshi_bot"

# Create backup directory
mkdir -p $BACKUP_DIR

# PostgreSQL backup
pg_dump -h localhost -U kalshi_user -d $DB_NAME > $BACKUP_DIR/kalshi_bot_$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/kalshi_bot_$TIMESTAMP.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to cloud storage (optional)
aws s3 cp $BACKUP_DIR/kalshi_bot_$TIMESTAMP.sql.gz s3://your-backup-bucket/database/
```

#### Database Optimization
```sql
-- Database maintenance queries
-- Run weekly via cron job

-- Update table statistics
ANALYZE;

-- Reindex tables
REINDEX DATABASE kalshi_bot;

-- Clean up old data (older than 1 year)
DELETE FROM trades WHERE created_at < NOW() - INTERVAL '1 year';
DELETE FROM market_data WHERE timestamp < NOW() - INTERVAL '1 year';

-- Vacuum tables
VACUUM ANALYZE trades;
VACUUM ANALYZE positions;
VACUUM ANALYZE market_data;
```

### Performance Monitoring

#### System Monitoring Script
```bash
#!/bin/bash
# scripts/monitor_system.sh

LOG_FILE="/var/log/kalshi-bot/system_monitor.log"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU usage
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Memory usage
    MEMORY=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')
    
    # Disk usage
    DISK=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    # Network connections
    CONNECTIONS=$(netstat -an | grep :8000 | wc -l)
    
    # Log metrics
    echo "$TIMESTAMP,CPU:$CPU%,Memory:$MEMORY%,Disk:$DISK%,Connections:$CONNECTIONS" >> $LOG_FILE
    
    # Alert if thresholds exceeded
    if (( $(echo "$CPU > 80" | bc -l) )); then
        echo "HIGH CPU USAGE: $CPU%" | mail -s "Kalshi Bot Alert" admin@yourcompany.com
    fi
    
    if (( $(echo "$MEMORY > 85" | bc -l) )); then
        echo "HIGH MEMORY USAGE: $MEMORY%" | mail -s "Kalshi Bot Alert" admin@yourcompany.com
    fi
    
    sleep 60
done
```

#### Application Performance Monitoring
```python
# src/monitoring/performance.py
import time
import functools
import logging
from typing import Callable, Any

performance_logger = logging.getLogger('performance')

def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            performance_logger.info(
                f"Function {func.__name__} executed in {execution_time:.4f}s"
            )
            
            # Alert on slow operations
            if execution_time > 5.0:
                performance_logger.warning(
                    f"Slow operation detected: {func.__name__} took {execution_time:.4f}s"
                )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            performance_logger.error(
                f"Function {func.__name__} failed after {execution_time:.4f}s: {str(e)}"
            )
            raise
            
    return wrapper

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        
    def record_metric(self, name: str, value: float, tags: dict = None):
        """Record a performance metric"""
        timestamp = time.time()
        self.metrics[name] = {
            'value': value,
            'timestamp': timestamp,
            'tags': tags or {}
        }
        
        performance_logger.info(
            f"Metric {name}: {value} {tags}"
        )
        
    def get_metrics(self) -> dict:
        """Get all recorded metrics"""
        return self.metrics
```

## Security Considerations

### API Security

#### Authentication and Authorization
```python
# src/api/auth.py
import jwt
import bcrypt
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps

class AuthManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        
    def generate_token(self, user_id: str, permissions: list) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
        
    def verify_token(self, token: str) -> dict:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")

def require_auth(permissions: list = None):
    """Decorator to require authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'No token provided'}), 401
                
            try:
                # Remove 'Bearer ' prefix
                token = token.replace('Bearer ', '')
                payload = auth_manager.verify_token(token)
                
                # Check permissions
                if permissions:
                    user_permissions = payload.get('permissions', [])
                    if not any(perm in user_permissions for perm in permissions):
                        return jsonify({'error': 'Insufficient permissions'}), 403
                        
                request.user = payload
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': str(e)}), 401
                
        return decorated_function
    return decorator
```

#### Rate Limiting
```python
# src/api/rate_limiting.py
import time
import redis
from flask import request, jsonify
from functools import wraps

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
        
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit"""
        current_time = int(time.time())
        window_start = current_time - window
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_requests = self.redis.zcard(key)
        
        if current_requests >= limit:
            return False
            
        # Add current request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window)
        
        return True

def rate_limit(requests_per_minute: int = 60):
    """Decorator to apply rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_ip = request.remote_addr
            user_id = getattr(request, 'user', {}).get('user_id', 'anonymous')
            key = f"rate_limit:{user_id}:{client_ip}"
            
            if not rate_limiter.is_allowed(key, requests_per_minute, 60):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': 60
                }), 429
                
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator
```

### Data Protection

#### Encryption Configuration
```python
# src/security/encryption.py
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DataEncryption:
    def __init__(self, password: str):
        self.password = password.encode()
        self.salt = os.urandom(16)
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
        
    def _derive_key(self) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
        
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
        
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()

# Usage for API keys and secrets
encryptor = DataEncryption(os.getenv('ENCRYPTION_PASSWORD'))
encrypted_api_key = encryptor.encrypt(os.getenv('KALSHI_API_KEY'))
```

#### Secure Configuration Management
```python
# src/security/config_manager.py
import os
import json
from typing import Any, Dict
from src.security.encryption import DataEncryption

class SecureConfigManager:
    def __init__(self, config_file: str, encryption_key: str):
        self.config_file = config_file
        self.encryptor = DataEncryption(encryption_key)
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load and decrypt configuration"""
        if not os.path.exists(self.config_file):
            return {}
            
        with open(self.config_file, 'r') as f:
            encrypted_config = json.load(f)
            
        config = {}
        for key, encrypted_value in encrypted_config.items():
            try:
                config[key] = self.encryptor.decrypt(encrypted_value)
            except Exception:
                # Handle non-encrypted values
                config[key] = encrypted_value
                
        return config
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
        self._save_config()
        
    def _save_config(self) -> None:
        """Encrypt and save configuration"""
        encrypted_config = {}
        for key, value in self._config.items():
            if key in ['KALSHI_API_KEY', 'KALSHI_API_SECRET', 'DATABASE_PASSWORD']:
                encrypted_config[key] = self.encryptor.encrypt(str(value))
            else:
                encrypted_config[key] = value
                
        with open(self.config_file, 'w') as f:
            json.dump(encrypted_config, f, indent=2)
```

### Network Security

#### SSL/TLS Configuration
```nginx
# nginx/ssl.conf
# Strong SSL configuration

ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Security headers
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' wss: https:;" always;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/ssl/chain.pem;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

#### Firewall Configuration
```bash
#!/bin/bash
# scripts/setup_firewall.sh

# Enable UFW
ufw --force enable

# Default policies
ufw default deny incoming
ufw default allow outgoing

# SSH access (change port as needed)
ufw allow 22/tcp

# HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Application ports (restrict to specific IPs if possible)
ufw allow from 10.0.0.0/8 to any port 8000  # API server
ufw allow from 10.0.0.0/8 to any port 5432  # PostgreSQL
ufw allow from 10.0.0.0/8 to any port 6379  # Redis

# Monitoring
ufw allow from 10.0.0.0/8 to any port 8001  # Metrics

# Rate limiting
ufw limit ssh

# Log dropped packets
ufw logging on

echo "Firewall configuration complete"
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Bot Not Starting
**Symptoms:**
- Application fails to start
- Error messages in logs
- Process exits immediately

**Diagnosis:**
```bash
# Check logs
tail -f logs/trading_bot.log

# Check process status
ps aux | grep python

# Check port availability
netstat -tulpn | grep :8000

# Check dependencies
pip list | grep -E "(requests|sqlalchemy|flask)"
```

**Solutions:**
1. **Missing Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Port Already in Use:**
   ```bash
   # Find process using port
   lsof -i :8000
   # Kill process
   kill -9 <PID>
   ```

3. **Database Connection Issues:**
   ```bash
   # Test database connection
   python -c "from src.core.database import DatabaseManager; db = DatabaseManager(); print('Connected')"
   ```

4. **API Credentials:**
   ```bash
   # Verify environment variables
   echo $KALSHI_API_KEY
   echo $KALSHI_API_SECRET
   ```

#### Issue: High Memory Usage
**Symptoms:**
- System becomes slow
- Out of memory errors
- Process killed by OOM killer

**Diagnosis:**
```bash
# Check memory usage
free -h
top -p $(pgrep -f "python src/main.py")

# Check for memory leaks
valgrind --tool=memcheck python src/main.py
```

**Solutions:**
1. **Optimize Model Loading:**
   ```python
   # Load models on demand instead of keeping in memory
   def get_model(model_name):
       if model_name not in self._loaded_models:
           self._loaded_models[model_name] = load_model(model_name)
       return self._loaded_models[model_name]
   ```

2. **Implement Caching:**
   ```python
   # Use LRU cache for frequently accessed data
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def get_market_data(market_id):
       return fetch_market_data(market_id)
   ```

3. **Garbage Collection:**
   ```python
   import gc
   
   # Force garbage collection periodically
   gc.collect()
   ```

#### Issue: Database Performance
**Symptoms:**
- Slow query execution
- High database CPU usage
- Connection timeouts

**Diagnosis:**
```sql
-- Check slow queries (PostgreSQL)
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Solutions:**
1. **Add Database Indexes:**
   ```sql
   -- Add indexes for frequently queried columns
   CREATE INDEX idx_trades_timestamp ON trades(timestamp);
   CREATE INDEX idx_positions_market_id ON positions(market_id);
   CREATE INDEX idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);
   ```

2. **Optimize Queries:**
   ```python
   # Use bulk operations instead of individual inserts
   def bulk_insert_trades(trades):
       db.session.bulk_insert_mappings(Trade, trades)
       db.session.commit()
   ```

3. **Connection Pooling:**
   ```python
   # Configure connection pool
   engine = create_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=30,
       pool_pre_ping=True,
       pool_recycle=3600
   )
   ```

#### Issue: API Rate Limiting
**Symptoms:**
- 429 Too Many Requests errors
- Delayed API responses
- Trading execution failures

**Diagnosis:**
```python
# Check API call frequency
import time
from collections import defaultdict

api_calls = defaultdict(list)

def track_api_call(endpoint):
    current_time = time.time()
    api_calls[endpoint].append(current_time)
    
    # Remove calls older than 1 minute
    api_calls[endpoint] = [
        t for t in api_calls[endpoint] 
        if current_time - t < 60
    ]
    
    print(f"API calls to {endpoint} in last minute: {len(api_calls[endpoint])}")
```

**Solutions:**
1. **Implement Exponential Backoff:**
   ```python
   import time
   import random
   
   def api_call_with_backoff(func, max_retries=5):
       for attempt in range(max_retries):
           try:
               return func()
           except RateLimitError:
               if attempt == max_retries - 1:
                   raise
               
               # Exponential backoff with jitter
               delay = (2 ** attempt) + random.uniform(0, 1)
               time.sleep(delay)
   ```

2. **Request Queuing:**
   ```python
   import queue
   import threading
   import time
   
   class APIRequestQueue:
       def __init__(self, max_requests_per_minute=60):
           self.queue = queue.Queue()
           self.max_requests = max_requests_per_minute
           self.request_times = []
           self.worker_thread = threading.Thread(target=self._worker)
           self.worker_thread.daemon = True
           self.worker_thread.start()
           
       def _worker(self):
           while True:
               request_func, result_queue = self.queue.get()
               
               # Rate limiting logic
               current_time = time.time()
               self.request_times = [
                   t for t in self.request_times 
                   if current_time - t < 60
               ]
               
               if len(self.request_times) >= self.max_requests:
                   sleep_time = 60 - (current_time - self.request_times[0])
                   time.sleep(sleep_time)
               
               # Execute request
               try:
                   result = request_func()
                   result_queue.put(('success', result))
               except Exception as e:
                   result_queue.put(('error', e))
               
               self.request_times.append(time.time())
               self.queue.task_done()
   ```

3. **Caching Strategy:**
   ```python
   import redis
   import json
   import time
   
   class APICache:
       def __init__(self, redis_client, default_ttl=300):
           self.redis = redis_client
           self.default_ttl = default_ttl
           
       def get_or_fetch(self, key, fetch_func, ttl=None):
           # Try to get from cache
           cached_data = self.redis.get(key)
           if cached_data:
               return json.loads(cached_data)
           
           # Fetch from API
           data = fetch_func()
           
           # Cache the result
           self.redis.setex(
               key, 
               ttl or self.default_ttl, 
               json.dumps(data)
           )
           
           return data
   ```

### Performance Optimization

#### Database Optimization
```sql
-- Optimize database configuration
-- postgresql.conf settings

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Connection settings
max_connections = 100
```

#### Application Optimization
```python
# src/optimization/performance.py
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Any

class PerformanceOptimizer:
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def parallel_api_calls(self, calls: List[Callable]) -> List[Any]:
        """Execute multiple API calls in parallel"""
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.executor, call)
            for call in calls
        ]
        return await asyncio.gather(*tasks)
        
    def batch_database_operations(self, operations: List[Callable]) -> None:
        """Batch database operations for better performance"""
        with DatabaseManager() as db:
            for operation in operations:
                operation(db)
            db.commit()
            
    def optimize_model_inference(self, texts: List[str]) -> List[float]:
        """Batch model inference for better GPU utilization"""
        # Process texts in batches
        batch_size = 32
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = self.sentiment_model.predict(batch)
            results.extend(batch_results)
            
        return results
```

This comprehensive deployment guide provides detailed instructions for deploying the Enhanced Kalshi Trading Bot in various environments, from local development to production cloud deployments. The guide covers all aspects of deployment, monitoring, security, and troubleshooting to ensure a successful and secure deployment.

