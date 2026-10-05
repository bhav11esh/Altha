# Conversation Service - Setup Guide

## Project Overview

The Conversation Service is a complete FastAPI application for managing medical conversations, extracting structured findings from AI responses, and maintaining immutable audit trails.

## Complete File Structure

```
conversation-service/
├── Core Application
│   ├── app.py                      # FastAPI application with all endpoints
│   ├── models.py                   # SQLAlchemy ORM models (4 tables)
│   ├── schemas.py                  # Pydantic validation models
│   ├── database.py                 # Database connection and initialization
│   ├── context_extractor.py        # Extract findings from AI responses
│   ├── turn_linker.py              # Link findings across turns
│   └── state_manager.py            # Persistence and state management
│
├── Database & Deployment
│   ├── init_db.sql                 # SQL schema (PostgreSQL)
│   ├── Dockerfile                  # Docker image definition
│   ├── docker-compose.yml          # Development Docker Compose
│   ├── docker-compose.prod.yml     # Production Docker Compose
│   └── nginx.conf                  # Production Nginx config
│
├── Testing & Examples
│   ├── test_client.py              # Python test client with demo
│   ├── test_conversation_service.sh # Bash test script with curl
│   └── sample_data.py              # Sample medical conversation data
│
├── Documentation
│   ├── README.md                   # Main project documentation
│   ├── API_USAGE_GUIDE.md          # Detailed API reference
│   ├── SETUP.md                    # This file
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment variables template
│
└── Configuration
    └── .gitignore                  # Git ignore rules
```

## Prerequisites

- Python 3.11 or higher
- Docker & Docker Compose (recommended) or PostgreSQL 15+
- curl or Postman for API testing
- Optional: jq for JSON parsing in bash scripts

## Installation Methods

### Method 1: Quick Start with Docker Compose (Recommended)

**Step 1: Navigate to project directory**
```bash
cd conversation-service
```

**Step 2: Start services**
```bash
docker-compose up -d
```

**Step 3: Verify services**
```bash
# Check if app is healthy
curl http://localhost:8000/health

# Check PostgreSQL
docker-compose ps
```

**Step 4: View logs**
```bash
docker-compose logs -f app
docker-compose logs -f db
```

**Done!** The service is running at `http://localhost:8000`

---

### Method 2: Local Development Setup

**Step 1: Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Step 2: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Set up PostgreSQL**

Option A: Install locally
```bash
# macOS
brew install postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15

# Start PostgreSQL service
sudo systemctl start postgresql
```

Option B: Use Docker for just the database
```bash
docker run -d \
  --name conversation_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=conversation_db \
  -p 5432:5432 \
  postgres:15-alpine
```

**Step 4: Configure environment**
```bash
cp .env.example .env
# Edit .env if using different credentials
export DATABASE_URL="postgresql://user:password@localhost:5432/conversation_db"
```

**Step 5: Initialize database**
```bash
python -c "from database import init_db; init_db()"
```

**Step 6: Run the application**
```bash
# Development with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Or with gunicorn for production-like testing
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

**Done!** The service is running at `http://localhost:8000`

---

### Method 3: Production Deployment with Docker Compose

**Step 1: Configure environment**
```bash
cp .env.example .env.prod
# Edit .env.prod with production credentials
```

**Step 2: Start production services**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Step 3: Configure Nginx (optional)**
```bash
# Create SSL certificates
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Nginx will serve on ports 80/443
```

**Step 4: Verify deployment**
```bash
curl https://localhost/health
```

---

## Verification Checklist

After installation, verify everything is working:

### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "conversation-service"}
```

### 2. API Documentation
Visit interactive documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Database Connection
```bash
# With Docker
docker-compose exec db psql -U user conversation_db

# Or directly if PostgreSQL is local
psql postgresql://user:password@localhost:5432/conversation_db
```

### 4. Run Test Script
```bash
chmod +x test_conversation_service.sh
./test_conversation_service.sh
```

### 5. Run Python Test Client
```bash
python test_client.py
```

---

## Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/conversation_db

# Application
PYTHONUNBUFFERED=1
```

### Database Configuration

Default credentials (docker-compose.yml):
- User: `user`
- Password: `password`
- Database: `conversation_db`
- Port: `5432`

Change in docker-compose.yml or use environment variables.

---

## First API Call

### Using curl
```bash
# Start a conversation
curl -X POST http://localhost:8000/conversations/start \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id_hash": "test_patient_001",
    "doctor_id": "dr_test_001"
  }'

# Response will include conversation ID
```

### Using Python
```python
import requests

api = "http://localhost:8000"

# Start conversation
resp = requests.post(f"{api}/conversations/start", json={
    "patient_id_hash": "test_patient_001",
    "doctor_id": "dr_test_001"
})
print(resp.json())
```

### Using the Test Client
```bash
python test_client.py
```

---

## Common Tasks

### View Application Logs

**With Docker Compose:**
```bash
docker-compose logs -f app
```

**Local development:**
```bash
# Logs appear in terminal where uvicorn is running
```

### Connect to Database

**With Docker:**
```bash
docker-compose exec db psql -U user conversation_db
```

**Local PostgreSQL:**
```bash
psql postgresql://user:password@localhost:5432/conversation_db
```

**Useful SQL queries:**
```sql
-- List all conversations
SELECT id, patient_id_hash, doctor_id, created_at FROM conversations;

-- List turns for a conversation
SELECT * FROM turns WHERE conversation_id = '...' ORDER BY turn_number;

-- List findings
SELECT finding_type, COUNT(*) FROM findings GROUP BY finding_type;

-- View audit logs
SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;
```

### Restart Services

**Docker Compose:**
```bash
docker-compose restart
```

### Stop Services

**Docker Compose:**
```bash
docker-compose down
```

### Clean Everything

**Docker Compose:**
```bash
docker-compose down -v  # -v removes volumes/data
```

---

## Testing the API

### Run All Tests

**Bash script (requires curl and jq):**
```bash
./test_conversation_service.sh
```

**Python client (requires requests):**
```bash
pip install requests
python test_client.py
```

### Sample Request/Response

**Request:**
```json
POST /turns/add HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_input": "Patient has headache and fever",
  "ai_response": "{"diagnosis": "Migraine", "drugs": ["Paracetamol"]}"
}
```

**Response:**
```json
{
  "turn_id": "660e8400-e29b-41d4-a716-446655440001",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "turn_number": 1,
  "timestamp": "2024-10-04T10:05:00",
  "findings_extracted": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "finding_type": "diagnosis",
      "value": "Migraine",
      "confidence": 1.0
    }
  ],
  "context_linked": false
}
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml or uvicorn command
uvicorn app:app --port 8001
```

### Database Connection Error

```bash
# Verify PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db

# Verify connection string
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Tables Not Created

```bash
# Reinitialize database
docker-compose exec app python -c "from database import init_db; init_db()"

# Or manually run SQL
docker-compose exec db psql -U user conversation_db < init_db.sql
```

### Memory Issues

For Docker:
```bash
# Increase Docker resources
docker-compose up -d --scale app=1
```

For local PostgreSQL:
```bash
# Increase PostgreSQL memory
# Edit postgresql.conf or set in SQL:
ALTER SYSTEM SET shared_buffers = '256MB';
```

### High CPU Usage

```bash
# Monitor container resources
docker stats

# Check if app is in tight loop
docker-compose logs app | tail -100

# Restart service
docker-compose restart app
```

---

## Performance Tips

### 1. Connection Pooling
Already configured with SQLAlchemy. For production, adjust:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,      # Connections per pool
    max_overflow=40,   # Temporary connections
    pool_pre_ping=True # Test connections before use
)
```

### 2. Database Indexing
Indexes are created in init_db.sql for:
- `conversations(patient_id_hash)`
- `turns(conversation_id, turn_number)`
- `findings(conversation_id, finding_type)`
- `audit_logs(turn_id, timestamp)`

### 3. Gunicorn Workers
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
# -w 4: 4 workers (adjust based on CPU cores)
```

### 4. Pagination
For large result sets:
```python
# Add to endpoints
limit = 50
offset = 0
results = query.limit(limit).offset(offset).all()
```

---

## Production Checklist

- [ ] Set strong database password
- [ ] Configure HTTPS/SSL certificates
- [ ] Enable authentication/authorization
- [ ] Set up logging and monitoring
- [ ] Configure backups
- [ ] Set up health checks
- [ ] Enable rate limiting
- [ ] Use secret management for credentials
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process
- [ ] Test disaster recovery
- [ ] Monitor resource usage

---

## Next Steps

1. **Read the README.md** for project overview
2. **Read API_USAGE_GUIDE.md** for detailed API reference
3. **Run test_client.py** to see working example
4. **Review sample_data.py** for example conversations
5. **Explore the code** in app.py, models.py, and related files
6. **Integrate with your system** using the Python client or HTTP calls

---

## Support & Troubleshooting

### Check Logs
```bash
# Docker
docker-compose logs [app|db]

# Local
# Check uvicorn terminal output
```

### Get Help
- Review API_USAGE_GUIDE.md for examples
- Check sample_data.py for sample conversations
- Run test_client.py for working demo
- Visit http://localhost:8000/docs for interactive API docs

### Common Issues
See "Troubleshooting" section above for solutions to:
- Port conflicts
- Database connection errors
- Missing tables
- Performance issues

---

## Project Information

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn / Gunicorn
- **Database**: PostgreSQL 15
- **Python**: 3.11+
- **License**: Part of Althea medical platform

---

**Installation complete!** Your Conversation Service is ready to use.
