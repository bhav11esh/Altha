# Environment Variables Guide

Complete reference for all environment variables used by Conversation Service.

## Quick Reference: Essential vs Optional

### REQUIRED (Must Configure)
```bash
DATABASE_URL                    # PostgreSQL connection string
```

### STRONGLY RECOMMENDED (For Production)
```bash
ENVIRONMENT=production
DEBUG=False
JWT_SECRET                      # Strong random key for tokens
ENCRYPTION_KEY                  # Base64-encoded 32-byte key
```

### OPTIONAL (By Feature)
```bash
OPENAI_API_KEY                 # Only if using OpenAI for LLM
ANTHROPIC_API_KEY              # Only if using Claude for LLM
REDIS_URL                      # Only if caching enabled
QDRANT_URL                     # Only if semantic search enabled
```

---

## Environment Variable Categories

### 1. DATABASE CONFIGURATION

| Variable | Default | Required | Purpose |
|----------|---------|----------|---------|
| `DATABASE_URL` | - | **YES** | PostgreSQL connection string |

**Examples:**
```bash
# Local development
DATABASE_URL=postgresql://user:password@localhost:5432/conversation_db

# Docker Compose
DATABASE_URL=postgresql://user:password@db:5432/conversation_db

# Production (AWS RDS)
DATABASE_URL=postgresql://user:pwd@mydb.c9akciq32.us-east-1.rds.amazonaws.com:5432/conversation_db
```

---

### 2. LLM PROVIDER KEYS

Choose ONE primary LLM provider, or configure multiple for fallback:

#### OpenAI (GPT-4, GPT-3.5-turbo)
```bash
OPENAI_API_KEY=sk-...           # Get from https://platform.openai.com/
OPENAI_MODEL=gpt-4              # Default model to use
OPENAI_ORG_ID=                  # Optional: organizational ID
```
**Cost**: ~$0.03-0.06 per 1K tokens (gpt-4)

#### Anthropic (Claude 3)
```bash
ANTHROPIC_API_KEY=sk-ant-...    # Get from console.anthropic.com
ANTHROPIC_MODEL=claude-3-opus-20240229
ANTHROPIC_MAX_TOKENS=4096
```
**Cost**: ~$0.015-0.075 per 1K tokens

#### Groq (Fast, cheap)
```bash
GROQ_API_KEY=gsk-...            # Get from console.groq.com
GROQ_MODEL=mixtral-8x7b-32768
```
**Cost**: Free tier available + paid

#### Google Gemini
```bash
GOOGLE_API_KEY=...              # Get from Google Cloud Console
GOOGLE_MODEL=gemini-pro
```

#### Azure OpenAI
```bash
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=your-deployment
AZURE_API_VERSION=2024-02-15-preview
```

**Decision Matrix:**
| Provider | Cost | Speed | Quality | Use Case |
|----------|------|-------|---------|----------|
| OpenAI (GPT-4) | $$ | Slow | ⭐⭐⭐⭐⭐ | Best quality, complex tasks |
| Anthropic (Claude 3 Opus) | $$ | Slow | ⭐⭐⭐⭐⭐ | Long context, safety |
| Groq | $ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Real-time, low latency |
| Google Gemini | $ | Medium | ⭐⭐⭐⭐ | Good for multimodal |

---

### 3. EMBEDDINGS & VECTOR DATABASES

For semantic similarity and finding matching:

#### Embeddings Provider
```bash
EMBEDDINGS_MODEL=text-embedding-3-small
EMBEDDINGS_PROVIDER=openai  # openai, huggingface, cohere
```

#### Qdrant (Vector Search)
```bash
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=                 # For cloud: https://cloud.qdrant.io
QDRANT_COLLECTION=medical_findings

# Docker Compose:
# docker run -p 6333:6333 qdrant/qdrant
```

#### Pinecone (Alternative)
```bash
PINECONE_API_KEY=...
PINECONE_ENV=production
PINECONE_INDEX=medical-index
```

---

### 4. CACHING & SESSIONS

For performance optimization:

```bash
# Redis (for conversation caching)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=                 # Optional: if password protected
REDIS_TTL=3600                 # Cache expiration (seconds)

# Session timeout
SESSION_TIMEOUT=1800           # 30 minutes
SESSION_REFRESH_INTERVAL=300   # Auto-refresh every 5 min
```

**Docker Compose Redis:**
```bash
# docker run -d -p 6379:6379 redis:latest
```

---

### 5. AUTHENTICATION & SECURITY

```bash
# API Authentication
API_KEY=your-secure-api-key-here
API_KEY_HEADER_NAME=X-API-Key

# JWT Tokens
JWT_SECRET=your-super-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Encryption (for PII at rest)
ENCRYPTION_KEY=base64-encoded-32-byte-key
```

**Generate Strong Keys:**
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Bash
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

---

### 6. NOTIFICATIONS & INTEGRATIONS

#### Email (SendGrid)
```bash
SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=noreply@example.com
```

#### SMS/WhatsApp (Twilio)
```bash
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_FROM_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

#### Slack Notifications
```bash
SLACK_BOT_TOKEN=xoxb-xxxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx
SLACK_CHANNEL=#alerts
```

---

### 7. MONITORING & ERROR TRACKING

#### Sentry (Error Tracking)
```bash
SENTRY_DSN=https://key@sentry.io/project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=1.0
```

#### Datadog
```bash
DATADOG_API_KEY=xxxxx
DATADOG_APP_KEY=xxxxx
DATADOG_SITE=datadoghq.com
```

#### New Relic
```bash
NEW_RELIC_LICENSE_KEY=xxxxx
NEW_RELIC_APP_NAME=conversation-service
```

---

### 8. FEATURE FLAGS

Control which features are enabled:

```bash
# Core features
ENABLE_FINDING_EXTRACTION=True          # Extract diagnoses, drugs, etc
ENABLE_CONTEXT_LINKING=True             # Link findings to previous turns
ENABLE_AUDIT_LOGGING=True               # Log all actions

# Performance features
ENABLE_FINDING_CACHING=True             # Cache extracted findings
ENABLE_SEMANTIC_SEARCH=False            # Use embeddings (requires setup)
ENABLE_LLM_ENHANCEMENT=False            # Use LLM to score findings

# Multi-language support
ENABLE_MULTI_LANGUAGE=False             # Support multiple languages
```

---

### 9. HEALTHCARE INTEGRATIONS

#### FHIR Server (HL7 Standard)
```bash
FHIR_SERVER_URL=https://fhir.example.com/
FHIR_SERVER_AUTH_TOKEN=Bearer xxxxx
```

#### EHR/EMR Integration
```bash
EHR_API_URL=https://ehr.example.com/api
EHR_API_KEY=xxxxx
EHR_PRACTICE_ID=12345
```

#### Drug & Disease Databases
```bash
DRUGS_DB_URL=https://api.drugs.com
DISEASE_DB_URL=https://disease.api
INTERACTION_CHECKER_URL=https://check.drugs.com/interactions
```

---

### 10. COMPLIANCE & SECURITY

```bash
# HIPAA Compliance
HIPAA_COMPLIANCE_MODE=True
ENCRYPT_PATIENT_DATA=True
ANONYMIZE_AUDIT_LOGS=False

# Data Retention
DATA_RETENTION_DAYS=2555               # ~7 years for HIPAA
AUTO_DELETE_EXPIRED_DATA=True

# PII Masking
MASK_PATIENT_ID=True
MASK_EMAIL=True
MASK_PHONE=True
```

---

## Setup Examples by Environment

### LOCAL DEVELOPMENT
```bash
# .env.local (for development only)
DATABASE_URL=postgresql://user:password@localhost:5432/conversation_db
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
OPENAI_API_KEY=sk-...  # Your OpenAI key for testing
JWT_SECRET=dev-secret-not-secure
ENCRYPTION_KEY=base64-encoded-32-byte-key
REDIS_URL=redis://localhost:6379/0
```

### DOCKER COMPOSE (Local)
```bash
# Already configured in docker-compose.yml
# Just set these if needed:
DATABASE_URL=postgresql://user:password@db:5432/conversation_db
OPENAI_API_KEY=sk-...
REDIS_URL=redis://redis:6379/0
```

### STAGING
```bash
DATABASE_URL=postgresql://user:pwd@staging-db.example.com:5432/conversation_db
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=INFO
OPENAI_API_KEY=sk-...
REDIS_URL=redis://staging-redis.example.com:6379/0
SENTRY_DSN=https://key@sentry.io/staging-project
JWT_SECRET=strong-staging-secret-32-chars
ENCRYPTION_KEY=base64-encoded-32-byte-key
```

### PRODUCTION
```bash
# Database (AWS RDS)
DATABASE_URL=postgresql://prod_user:prod_pwd@prod-db.xxxxx.rds.amazonaws.com:5432/conversation_db

# Application
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING
ALLOWED_ORIGINS=https://app.example.com,https://api.example.com

# LLM (Production model)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Caching & Speed
REDIS_URL=redis://prod-redis.example.com:6379/0
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=qdrant-api-key

# Security
JWT_SECRET=super-secure-production-key-minimum-32-chars
ENCRYPTION_KEY=base64-encoded-32-byte-key-production

# Monitoring
SENTRY_DSN=https://key@sentry.io/production-project
DATADOG_API_KEY=xxxxx
NEW_RELIC_LICENSE_KEY=xxxxx

# Notifications
SENDGRID_API_KEY=SG.xxxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxxxx

# Healthcare
FHIR_SERVER_URL=https://fhir.production.com/
EHR_API_KEY=xxxxx

# Compliance
HIPAA_COMPLIANCE_MODE=True
ENCRYPT_PATIENT_DATA=True
```

---

## How to Set Environment Variables

### Method 1: `.env.local` File (Development)
```bash
cp .env.example .env.local
# Edit .env.local with your values
```

### Method 2: Shell Export (Quick Testing)
```bash
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."
uvicorn app:app
```

### Method 3: Docker Environment
```bash
# In docker-compose.yml
environment:
  DATABASE_URL: postgresql://user:password@db:5432/conversation_db
  OPENAI_API_KEY: sk-xxx
```

### Method 4: Kubernetes Secrets
```bash
kubectl create secret generic conversation-service \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=OPENAI_API_KEY='sk-...'
```

### Method 5: CI/CD (GitHub Actions)
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Validation Checklist

Before deploying, verify:

- [ ] `DATABASE_URL` is set and PostgreSQL is accessible
- [ ] At least one LLM key is configured (OpenAI, Claude, etc)
- [ ] `JWT_SECRET` is a strong random string (32+ chars)
- [ ] `ENCRYPTION_KEY` is base64-encoded 32-byte key
- [ ] `ENVIRONMENT` is set to `production` (not development)
- [ ] `DEBUG=False` in production
- [ ] `REDIS_URL` points to valid Redis instance (if caching enabled)
- [ ] All external API keys are valid
- [ ] `ALLOWED_ORIGINS` is set to your frontend domains
- [ ] Sensitive keys are in `.env.local` or secrets manager (NOT git)
- [ ] Log level is appropriate for your environment
- [ ] HIPAA compliance flags are set correctly

---

## Troubleshooting

### "Database connection failed"
```bash
# Test PostgreSQL connection
psql $DATABASE_URL -c "SELECT 1"

# Check Docker container
docker-compose ps
docker-compose logs db
```

### "OpenAI API key invalid"
```bash
# Verify key format (should start with sk-)
echo $OPENAI_API_KEY

# Test API call
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### "Redis connection refused"
```bash
# Test Redis
redis-cli -u $REDIS_URL ping

# Start Redis if needed
docker run -d -p 6379:6379 redis:latest
```

### "JWT token invalid"
```bash
# Regenerate JWT_SECRET
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Security Best Practices

1. **Never commit `.env.local`** - Add to `.gitignore`
2. **Use strong secrets** - Minimum 32 characters
3. **Rotate keys regularly** - Especially in production
4. **Use secrets manager** - AWS Secrets Manager, HashiCorp Vault
5. **Limit API key scope** - Create restricted keys for each service
6. **Monitor usage** - Set up alerts for unusual API activity
7. **Encrypt at rest** - Use ENCRYPTION_KEY for sensitive data
8. **HTTPS only** - Use in production
9. **Enable audit logging** - ENABLE_AUDIT_LOGGING=True
10. **Regular backups** - Backup database and encryption keys

