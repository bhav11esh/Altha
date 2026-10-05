# Installation Guide - Medical AI

Complete step-by-step instructions for setting up Medical AI locally or in production.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Local Development Setup](#local-development-setup)
3. [Docker Setup](#docker-setup)
4. [Production Deployment](#production-deployment)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **OS**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **RAM**: 4GB minimum
- **Storage**: 2GB for dependencies and database

### Recommended

- **Python**: 3.11+
- **Node.js**: 18+
- **RAM**: 8GB+
- **Storage**: SSD with 10GB+ free space
- **Database**: PostgreSQL 14+ (for production)

### Optional

- **Docker**: 20.10+ with Docker Compose
- **Git**: For version control
- **Make**: For simplified commands

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd openwebui-medical
```

### Step 2: Backend Setup

#### Create Virtual Environment

```bash
cd backend
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Database
DATABASE_URL=sqlite:///./medical_ai.db

# Security (change for production!)
SECRET_KEY=dev-secret-key-change-in-production

# CrewAI Backend
CREWAI_BACKEND_URL=http://localhost:8001
```

#### Initialize Database

```bash
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

#### Start Backend Server

```bash
python app.py
```

Backend will be available at `http://localhost:8000`

**Verify it's running:**
```bash
curl http://localhost:8000/health
```

### Step 3: Frontend Setup

Open a new terminal in the `frontend` directory:

```bash
cd openwebui-medical/frontend
```

#### Install Dependencies

```bash
npm install
```

#### Configure Environment

```bash
echo "VITE_API_URL=http://localhost:8000" > .env
```

#### Start Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Step 4: Test the Setup

1. Open browser: `http://localhost:5173`
2. Register a new account
3. Create a conversation
4. Send a test message

## Docker Setup

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Quick Start

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

Access:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Common Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Access backend container shell
docker-compose exec backend sh
```

### Custom Configuration

Create `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/medical_ai
      - SECRET_KEY=your-production-secret-key

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: medical_ai
      POSTGRES_USER: medicalai
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres-data:
```

## Production Deployment

### 1. Server Setup

#### Ubuntu/Debian

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  nodejs \
  npm \
  postgresql \
  postgresql-contrib \
  nginx \
  certbot \
  python3-certbot-nginx

# Install Docker (optional but recommended)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### Create Application User

```bash
sudo useradd -m -s /bin/bash medicalai
sudo -u medicalai mkdir -p /home/medicalai/app
cd /home/medicalai/app
sudo chown medicalai:medicalai .
```

### 2. Database Setup

#### PostgreSQL Configuration

```bash
sudo -u postgres psql

-- In psql:
CREATE USER medicalai WITH PASSWORD 'secure_password_here';
CREATE DATABASE medical_ai WITH OWNER medicalai;
GRANT ALL PRIVILEGES ON DATABASE medical_ai TO medicalai;
\q
```

### 3. Application Deployment

#### Clone and Setup

```bash
sudo -u medicalai git clone <repository-url> /home/medicalai/app/medical-ai
cd /home/medicalai/app/medical-ai
```

#### Backend Deployment

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production .env
cat > .env << EOF
DATABASE_URL=postgresql://medicalai:password@localhost:5432/medical_ai
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
CREWAI_BACKEND_URL=http://localhost:8001
EOF

# Initialize database
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

#### Frontend Deployment

```bash
cd ../frontend
npm install
npm run build
```

### 4. Systemd Services

Create `/etc/systemd/system/medical-ai-backend.service`:

```ini
[Unit]
Description=Medical AI Backend
After=network.target postgresql.service

[Service]
Type=notify
User=medicalai
WorkingDirectory=/home/medicalai/app/medical-ai/backend
Environment="PATH=/home/medicalai/app/medical-ai/backend/venv/bin"
ExecStart=/home/medicalai/app/medical-ai/backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/medical-ai-frontend.service`:

```ini
[Unit]
Description=Medical AI Frontend
After=network.target

[Service]
Type=simple
User=medicalai
WorkingDirectory=/home/medicalai/app/medical-ai/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start services:

```bash
sudo systemctl daemon-reload
sudo systemctl enable medical-ai-backend.service
sudo systemctl enable medical-ai-frontend.service
sudo systemctl start medical-ai-backend.service
sudo systemctl start medical-ai-frontend.service

# Check status
sudo systemctl status medical-ai-backend.service
sudo systemctl status medical-ai-frontend.service
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/medical-ai`:

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:5173;
}

server {
    listen 80;
    server_name medical-ai.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name medical-ai.example.com;

    ssl_certificate /etc/letsencrypt/live/medical-ai.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/medical-ai.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API proxy
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/medical-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate

```bash
sudo certbot certonly --nginx -d medical-ai.example.com
```

## Configuration

### Backend Configuration

Environment variables in `backend/.env`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///./medical_ai.db` | Database connection string |
| `SECRET_KEY` | `change-in-production` | JWT signing key (64+ chars) |
| `CREWAI_BACKEND_URL` | `http://localhost:8001` | CrewAI service URL |
| `ANTHROPIC_API_KEY` | `` | Anthropic API key (optional) |

### Frontend Configuration

Environment variables in `frontend/.env`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |

## Database Migration

### From SQLite to PostgreSQL

```bash
# Export SQLite
sqlite3 backend/medical_ai.db .dump > dump.sql

# Import to PostgreSQL
psql medical_ai < dump.sql
```

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

```bash
# Solution: Install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `sqlite3.OperationalError: unable to open database file`

```bash
# Solution: Check directory permissions
chmod -R 755 backend/
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

### Frontend Won't Connect

**Error**: `ERR_CONNECTION_REFUSED`

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check VITE_API_URL in .env
cat frontend/.env
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port by modifying app.py line: uvicorn.run(..., port=8001)
```

### Permission Denied

```bash
# Make scripts executable
chmod +x start.sh

# Fix file ownership
sudo chown -R $USER:$USER openwebui-medical/
```

### Database Lock

```bash
# Remove lock file
rm backend/medical_ai.db-journal

# For PostgreSQL connection issues
psql -h localhost -U medicalai medical_ai -c "SELECT 1;"
```

## Monitoring

### System Health

```bash
# Backend health
curl http://localhost:8000/health

# Check logs
tail -f backend/logs/app.log

# Monitor system resources
watch -n 1 'free -h && du -sh .'
```

### Database Health

```bash
# PostgreSQL
psql medical_ai -c "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database WHERE datname='medical_ai';"

# Check connections
psql medical_ai -c "SELECT usename, count(*) FROM pg_stat_activity GROUP BY usename;"
```

## Backup & Restore

### SQLite Backup

```bash
# Backup
cp backend/medical_ai.db backend/medical_ai.db.backup

# Restore
cp backend/medical_ai.db.backup backend/medical_ai.db
```

### PostgreSQL Backup

```bash
# Full backup
pg_dump medical_ai > backup.sql

# Compressed backup
pg_dump medical_ai | gzip > backup.sql.gz

# Restore
psql medical_ai < backup.sql
```

## Updates

### Update Backend

```bash
cd backend
source venv/bin/activate
git pull
pip install -r requirements.txt
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
sudo systemctl restart medical-ai-backend.service
```

### Update Frontend

```bash
cd frontend
git pull
npm install
npm run build
sudo systemctl restart medical-ai-frontend.service
```

## Security Checklist

- [ ] Change `SECRET_KEY` to random 64+ character string
- [ ] Use PostgreSQL in production (not SQLite)
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure firewall rules
- [ ] Set up regular database backups
- [ ] Enable audit logging
- [ ] Configure CORS properly
- [ ] Use environment variable management
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Set up rate limiting
- [ ] Use strong database passwords

## Support

For issues:

1. Check this guide first
2. Review logs: `docker-compose logs`
3. Test API: `curl http://localhost:8000/docs`
4. Check configuration files
5. Verify database connectivity
6. Review system resources

---

**Version**: 1.0.0  
**Last Updated**: 2024
