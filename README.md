# MediAI - Medical AI Platform

A comprehensive medical AI platform that leverages CrewAI agents, vector databases, and conversational interfaces to provide intelligent medical assistance and insights.

## Overview

MediAI is a Docker-based microservices platform designed for medical AI applications. It integrates multiple specialized services working together to provide seamless medical data analysis, conversation management, and API integration.

## Technology Stack

- **Python 3.11** - Backend services (FastAPI/Uvicorn)
- **Node.js 18** - Frontend application
- **PostgreSQL 15** - Primary database
- **Redis 7** - Caching and session management
- **Qdrant** - Vector database for embeddings and semantic search
- **Docker & Docker Compose** - Containerization and orchestration
- **Nginx** - Reverse proxy and frontend serving
- **CrewAI** - AI agent framework

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MediAI Platform                          │
└─────────────────────────────────────────────────────────────┘

                      ┌──────────────┐
                      │  OpenWebUI   │ (Port 3000/8000)
                      │  Frontend    │
                      └──────┬───────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼─────┐       ┌─────▼──────┐    ┌──────▼────┐
    │ CrewAI   │       │ Conversation│    │ API       │
    │ Service  │       │ Service     │    │ Integration
    │(8001)    │       │ (8002)      │    │(8003)
    └────┬─────┘       └─────┬──────┘    └──────┬────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼─────┐       ┌─────▼──────┐    ┌──────▼────┐
    │PostgreSQL│       │   Redis    │    │ Qdrant    │
    │ Database │       │   Cache    │    │ Vectors   │
    │ (5432)   │       │ (6379)     │    │(6333)     │
    └──────────┘       └────────────┘    └───────────┘
```

## Services

### 1. **OpenWebUI Medical** (Port 3000/8000)
   - Web-based user interface for medical AI interactions
   - Frontend: React/Vue.js application
   - Backend: Python FastAPI service
   - Serves static assets and API proxy

### 2. **CrewAI Service** (Port 8001)
   - AI agent framework for task execution
   - Multi-agent orchestration
   - Task planning and execution
   - Medical domain-specific workflows

### 3. **Conversation Service** (Port 8002)
   - Manages conversation history
   - Context management
   - Message routing
   - Session persistence

### 4. **API Integration Service** (Port 8003)
   - Integrates external medical APIs
   - Data transformation and validation
   - FHIR compliance
   - Rate limiting and caching

### 5. **PostgreSQL** (Port 5432)
   - Primary relational database
   - User data, conversations, medical records
   - Transactions and ACID compliance

### 6. **Redis** (Port 6379)
   - In-memory cache
   - Session management
   - Rate limiting
   - Real-time data

### 7. **Qdrant** (Port 6333)
   - Vector database
   - Medical embeddings storage
   - Semantic search
   - Similar document retrieval

## Quick Start

### Prerequisites
- Docker (v20.10+)
- Docker Compose (v1.29+)
- Git
- 4GB RAM minimum
- 10GB disk space

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mediai
   ```

2. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services**
   ```bash
   docker-compose up -d
   ```

4. **Verify all services are running**
   ```bash
   docker-compose ps
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8003
   - Backend API: http://localhost:8000

### Health Checks

All services include health check endpoints:

```bash
# Check individual services
curl http://localhost:8001/health   # CrewAI
curl http://localhost:8002/health   # Conversation Service
curl http://localhost:8003/health   # API Integration
curl http://localhost:3000/health   # OpenWebUI Frontend
curl http://localhost:8000/health   # OpenWebUI Backend

# Check database services
docker-compose exec postgres pg_isready -U mediai
docker-compose exec redis redis-cli ping
```

## Development Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f crewai
docker-compose logs -f conversation-service
docker-compose logs -f api-integration

# Last 100 lines
docker-compose logs --tail=100 crewai
```

### Access Service Shells

```bash
# Python services
docker-compose exec crewai bash
docker-compose exec conversation-service bash
docker-compose exec api-integration bash

# Database access
docker-compose exec postgres psql -U mediai -d mediai
docker-compose exec redis redis-cli
```

### Restart Services

```bash
# Single service
docker-compose restart crewai

# All services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build crewai
```

### Stop Services

```bash
# Stop all without removing
docker-compose stop

# Stop specific service
docker-compose stop crewai

# Stop and remove (keeps volumes)
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

## Environment Variables

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://mediai:devpassword@postgres:5432/mediai
POSTGRES_USER=mediai
POSTGRES_PASSWORD=devpassword

# Cache
REDIS_URL=redis://redis:6379

# Vector DB
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=qdrant-key

# Service URLs (internal communication)
CREWAI_URL=http://crewai:8001
CONVERSATION_SERVICE_URL=http://conversation-service:8002
API_INTEGRATION_URL=http://api-integration:8003

# API Keys
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Logging
LOG_LEVEL=INFO
NODE_ENV=production
```

## Database Initialization

Databases are automatically initialized on first run. To manually initialize:

```bash
# Run migrations
docker-compose exec api-integration python manage.py migrate

# Seed sample data
docker-compose exec api-integration python manage.py seed_data
```

## API Endpoints

### CrewAI Service
```
POST   /api/agents          - List available agents
POST   /api/tasks           - Create and execute task
GET    /api/tasks/{id}      - Get task status
POST   /api/agents/execute  - Execute agent workflow
```

### Conversation Service
```
POST   /api/conversations        - Create conversation
GET    /api/conversations        - List conversations
GET    /api/conversations/{id}   - Get conversation
POST   /api/conversations/{id}/messages - Send message
GET    /api/conversations/{id}/messages - Get messages
```

### API Integration
```
GET    /api/health          - Health check
POST   /api/patients        - Create patient record
GET    /api/patients/{id}   - Get patient data
POST   /api/fhir/validate   - Validate FHIR resource
```

## Production Deployment

### Environment Variables for Production
```env
# Security
NODE_ENV=production
LOG_LEVEL=WARN
DEBUG=false

# Database
DATABASE_URL=postgresql://produser:securepass@db-host:5432/mediai
POSTGRES_SSL_MODE=require

# API Keys (use secrets management)
OPENAI_API_KEY=<from-secrets>
ANTHROPIC_API_KEY=<from-secrets>

# Domain
OPENWEBUI_API_BASE=https://api.mediai.com
VITE_API_BASE_URL=https://api.mediai.com
```

### Docker Compose Production
```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale crewai=3 --scale conversation-service=2
```

### Health Monitoring
```bash
# Docker health status
docker-compose ps

# Container metrics
docker stats mediai-*

# Service logs with timestamps
docker-compose logs --timestamps -f
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs crewai

# Verify port availability
netstat -tuln | grep LISTEN

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Database connection issues
```bash
# Test PostgreSQL connection
docker-compose exec postgres psql -U mediai -c "SELECT version();"

# Check Redis connection
docker-compose exec redis redis-cli ping
```

### Performance issues
```bash
# Check resource usage
docker stats

# Increase service limits in docker-compose.yml
# Add under service:
# deploy:
#   resources:
#     limits:
#       cpus: '2'
#       memory: 2G
```

### Memory issues
```bash
# Check container memory
docker stats mediai-postgres

# Reduce Redis memory
docker-compose exec redis CONFIG SET maxmemory 512mb
```

## File Structure

```
.
├── docker-compose.yml          # Compose orchestration
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── Makefile                   # Development commands
├── README.md                  # This file
├── crewai-backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── conversation-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── api-integration/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── openwebui-medical/
    ├── Dockerfile
    ├── nginx.conf
    ├── backend/
    │   ├── requirements.txt
    │   └── app.py
    └── frontend/
        ├── package.json
        └── src/
```

## Contributing

1. Create a feature branch
2. Make changes
3. Test in Docker environment
4. Submit pull request

## Security Considerations

- Never commit `.env` file
- Use strong database passwords in production
- Enable SSL/TLS for API endpoints
- Implement API authentication/authorization
- Regular security updates for base images
- Monitor container logs for security events
- Use secrets management for API keys

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review architecture diagram above
- Consult service-specific documentation
- Check GitHub issues

## License

Proprietary - MediAI Platform

---

**Last Updated**: 2024
**Version**: 1.0.0
