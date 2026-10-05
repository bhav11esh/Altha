# MediAI Deployment Guide

This guide covers deployment strategies for the MediAI platform across different environments.

## Deployment Environments

### Local Development
```bash
# Setup
cp .env.example .env
docker-compose up -d --build

# Access
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API: http://localhost:8003
```

### Development with Live Reload
```bash
# Use development compose file for hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Watch logs
make logs
```

### Production Deployment
```bash
# Prepare production environment
cp .env.example .env.prod
# Edit .env.prod with production values

# Deploy with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  --env-file .env.prod up -d

# Or use the Makefile
make up-prod
```

## Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Database credentials configured
- [ ] API keys set in `.env`
- [ ] OPENAI_API_KEY configured
- [ ] ANTHROPIC_API_KEY configured
- [ ] Domain/URL configured
- [ ] SSL certificates prepared
- [ ] Redis password secured
- [ ] PostgreSQL password hardened

### 2. Infrastructure
- [ ] Sufficient disk space (10GB minimum)
- [ ] RAM available (4GB minimum)
- [ ] Network connectivity verified
- [ ] Docker and Docker Compose installed
- [ ] Port 3000, 8000, 8001, 8002, 8003 available
- [ ] Database backups configured

### 3. Security
- [ ] Firewall rules configured
- [ ] HTTPS enabled
- [ ] API authentication configured
- [ ] Database SSL enabled
- [ ] Secret management in place
- [ ] Network policies defined

## Deployment Scripts

### Quick Start
```bash
./scripts/deploy.sh production
```

### Health Check
```bash
./scripts/health-check.sh
```

### Backup Database
```bash
./scripts/backup-db.sh
```

### Rollback
```bash
./scripts/rollback.sh <previous-version>
```

## Database Migrations

### Initial Setup
```bash
docker-compose exec api-integration python manage.py migrate
docker-compose exec api-integration python manage.py seed_data
```

### Running Migrations
```bash
docker-compose exec api-integration alembic upgrade head
```

### Rollback Migration
```bash
docker-compose exec api-integration alembic downgrade -1
```

## Scaling

### Horizontal Scaling
```bash
# Scale specific services
docker-compose up -d --scale crewai=3 --scale api-integration=2

# With service limits
docker-compose -f docker-compose.prod.yml up -d
```

### Resource Limits
Edit `docker-compose.prod.yml`:
```yaml
services:
  crewai:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
```

## Monitoring

### Container Metrics
```bash
docker stats mediai-*
```

### Log Aggregation
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f crewai --tail=100
```

### Health Endpoints
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:3000/health
```

## Backup & Recovery

### Database Backup
```bash
docker-compose exec postgres pg_dump -U mediai mediai > backup.sql
```

### Database Restore
```bash
docker-compose exec -T postgres psql -U mediai mediai < backup.sql
```

### Volume Backup
```bash
docker run --rm -v postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_data.tar.gz /data
```

## Update Procedures

### Rolling Update
```bash
# Update single service without downtime
docker-compose up -d --no-deps --build crewai
docker-compose exec crewai /app/scripts/migrate.sh
```

### Blue-Green Deployment
```bash
# Deploy new version alongside current
docker tag mediai-crewai:latest mediai-crewai:blue
docker-compose up -d --build mediai-crewai-green

# Switch traffic after verification
docker service update --image mediai-crewai:green mediai-crewai
```

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs crewai

# Verify configuration
docker-compose config

# Test service connectivity
docker-compose exec postgres pg_isready -U mediai
```

### Out of Disk Space
```bash
# Clean up
docker system prune -a --volumes

# Check usage
docker system df
```

### Database Connection Issues
```bash
# Test connection
docker-compose exec postgres \
  psql -U mediai -d mediai -c "SELECT version();"

# Check logs
docker-compose logs postgres
```

## Performance Tuning

### PostgreSQL Optimization
```sql
-- Inside postgres container
VACUUM ANALYZE;
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CLUSTER conversations USING idx_conversations_user_id;
```

### Redis Optimization
```bash
# Monitor commands
docker-compose exec redis redis-cli monitor

# Analyze memory
docker-compose exec redis redis-cli info memory
```

## Compliance & Security

### HIPAA Compliance
- [ ] Encryption at rest
- [ ] Encryption in transit (TLS 1.2+)
- [ ] Access logging enabled
- [ ] Audit trails maintained
- [ ] Data retention policies enforced

### GDPR Compliance
- [ ] Data export functionality
- [ ] Right to be forgotten implemented
- [ ] Consent tracking
- [ ] Privacy policy in place

## Maintenance Schedule

### Daily
- Monitor logs
- Check service health
- Verify backups

### Weekly
- Database optimization
- Performance analysis
- Security updates

### Monthly
- Full system tests
- Capacity planning
- Documentation updates

### Quarterly
- Security audit
- Performance tuning
- Disaster recovery drill
