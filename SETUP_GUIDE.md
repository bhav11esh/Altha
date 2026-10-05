# MediAI Setup Guide

Complete setup instructions for the MediAI platform deployment.

## Prerequisites

### System Requirements
- **Docker**: 20.10 or higher
- **Docker Compose**: 1.29 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 10GB minimum (20GB recommended)
- **OS**: Linux, macOS, or Windows (with WSL2)

### Installation Links
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Verify Installation
```bash
docker --version
docker-compose --version
```

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
# Navigate to project directory
cd /path/to/mediai

# Copy environment template
cp .env.example .env

# Start all services
docker-compose up -d
```

### 2. Wait for Services
```bash
# Check service status
docker-compose ps

# Watch logs
docker-compose logs -f
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Integration**: http://localhost:8003

## Detailed Setup

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd mediai
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings (required)
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - Database passwords (production only)

# Verify configuration
cat .env
```

### Step 3: Build Images (Optional)
Pre-built images are used by default. To build locally:
```bash
docker-compose build
# or specific service
docker-compose build crewai
```

### Step 4: Start Services
```bash
# Start in background
docker-compose up -d

# Or view logs while starting
docker-compose up
```

### Step 5: Verify Health
```bash
# Check all services
make health

# Or manually
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:3000/health
```

## Common Setup Issues

### Port Already in Use
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

### Docker Daemon Not Running
```bash
# macOS/Windows - Start Docker Desktop
open -a Docker

# Linux - Start Docker service
sudo systemctl start docker
```

### Insufficient Disk Space
```bash
# Clean up Docker
docker system prune -a --volumes

# Check available space
docker system df
```

### Out of Memory
```bash
# Check memory allocation
docker stats

# Increase Docker memory allocation in Docker Desktop settings
# Settings → Resources → Memory
```

## Post-Installation

### Initialize Database
```bash
# Run database migrations
docker-compose exec api-integration python -m alembic upgrade head

# Seed sample data (optional)
docker-compose exec api-integration python -m scripts.seed_data
```

### Create Admin User
```bash
docker-compose exec openwebui python manage.py createsuperuser
```

### Test API
```bash
# Test CrewAI Service
curl -X GET http://localhost:8001/api/agents

# Test Conversation Service
curl -X GET http://localhost:8002/api/conversations

# Test API Integration
curl -X GET http://localhost:8003/api/medical-providers
```

## Development Setup

### Enable Hot Reload
```bash
# Use development compose file
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Changes to code auto-reload
```

### Access Service Shells
```bash
# Python shell
docker-compose exec crewai python

# Bash shell
docker-compose exec crewai bash

# PostgreSQL
docker-compose exec postgres psql -U mediai -d mediai

# Redis CLI
docker-compose exec redis redis-cli
```

### View Real-Time Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f crewai --tail=100

# Follow logs for multiple services
docker-compose logs -f crewai conversation-service api-integration
```

## Production Setup

### Environment Configuration
```bash
# Create production environment file
cp .env.example .env.prod

# Edit with production values
nano .env.prod

# Critical settings:
# - POSTGRES_PASSWORD (strong password)
# - OPENAI_API_KEY (valid key)
# - QDRANT_API_KEY (strong key)
# - NODE_ENV=production
# - LOG_LEVEL=WARN
```

### Deploy to Production
```bash
# Use production compose file
docker-compose -f docker-compose.yml \
  -f docker-compose.prod.yml \
  --env-file .env.prod \
  up -d

# Or use Makefile
make up-prod
```

### Backup Before Production
```bash
# Backup volumes
docker run --rm -v postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Monitoring Setup
```bash
# Enable metrics collection
docker-compose exec crewai pip install prometheus-client

# Check container metrics
docker stats mediai-*
```

## Configuration Reference

### Essential Environment Variables

```env
# Database (required)
DATABASE_URL=postgresql://mediai:password@postgres:5432/mediai
POSTGRES_USER=mediai
POSTGRES_PASSWORD=devpassword
POSTGRES_DB=mediai

# Redis (required)
REDIS_URL=redis://redis:6379

# Qdrant (required)
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=your-api-key

# AI Services (required for functionality)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Service URLs (use defaults unless custom networking)
CREWAI_URL=http://crewai:8001
CONVERSATION_SERVICE_URL=http://conversation-service:8002
API_INTEGRATION_URL=http://api-integration:8003

# Logging
LOG_LEVEL=INFO (DEBUG for development)
NODE_ENV=production (development for dev)
```

## Verification Checklist

- [ ] Docker and Docker Compose installed
- [ ] .env file configured with API keys
- [ ] All services started: `docker-compose ps`
- [ ] Health endpoints responding
- [ ] Frontend accessible at port 3000
- [ ] Database initialized
- [ ] Redis responding to PING
- [ ] Qdrant admin panel accessible (port 6333)

## Next Steps

1. **Configure API Keys**
   - Get OpenAI API key
   - Get Anthropic API key
   - Update .env file

2. **Customize for Your Use Case**
   - Add custom agents to CrewAI
   - Integrate external APIs
   - Configure conversation templates

3. **Set Up Monitoring**
   - Enable log aggregation
   - Configure health monitoring
   - Set up alerts

4. **Deploy to Production**
   - Follow DEPLOYMENT.md
   - Set up SSL/TLS
   - Configure backups

## Getting Help

### Check Logs
```bash
docker-compose logs -f crewai
docker-compose logs -f conversation-service
docker-compose logs -f api-integration
```

### Restart Services
```bash
# Single service
docker-compose restart crewai

# All services
docker-compose restart

# Force rebuild
docker-compose up -d --build crewai
```

### Clean Restart
```bash
# Stop and remove everything
docker-compose down -v

# Start fresh
docker-compose up -d
```

## Additional Resources

- [README.md](./README.md) - Project overview
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment
- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

**Version**: 1.0.0  
**Last Updated**: 2024
