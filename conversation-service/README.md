# Conversation Service - Medical Context Manager

A FastAPI-based medical conversation context manager that extracts structured findings from AI responses and maintains immutable audit trails for medical conversations.

## Features

- **Conversation Management**: Start and manage medical conversations between doctors and patients
- **Context Extraction**: Automatically extract diagnoses, drugs, recommendations, and lab tests from AI responses
- **Turn Linking**: Link findings from current turns to previous context and findings
- **Immutable Audit Trail**: Track all actions with timestamps and details for compliance
- **Enriched Context**: Get previous findings and related context for each turn
- **Finding Chains**: Analyze chains of related findings across conversation turns
- **PostgreSQL Backend**: Persistent storage with proper indexing and relationships

## Quick Start

### Setup with Docker Compose (Recommended)

```bash
cd conversation-service
docker-compose up -d
curl http://localhost:8000/health
```

The app will be available at `http://localhost:8000`

### Setup Locally

```bash
pip install -r requirements.txt
export DATABASE_URL=postgresql://user:password@localhost:5432/conversation_db
python -c "from database import init_db; init_db()"
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Core Modules

- **models.py**: SQLAlchemy ORM models (Conversation, Turn, Finding, AuditLog)
- **schemas.py**: Pydantic request/response models
- **database.py**: PostgreSQL connection and initialization
- **context_extractor.py**: Parse AI responses and extract findings
- **turn_linker.py**: Link findings to previous context
- **state_manager.py**: Persistence logic
- **app.py**: FastAPI application with all endpoints

## API Endpoints

### Conversation Management
- `POST /conversations/start` - Create new conversation
- `POST /turns/add` - Add turn with auto context extraction
- `GET /turns/{conversation_id}` - Get all turns
- `GET /context/{turn_id}?conversation_id={conv_id}` - Get enriched context
- `GET /findings/{conversation_id}` - Get all findings
- `GET /audit/{turn_id}` - Get turn audit log
- `GET /audit/conversation/{conversation_id}` - Get conversation audit trail
- `GET /context-chains/{conversation_id}` - Get finding chains

## Database Schema

```
conversations
  ├── id (UUID)
  ├── patient_id_hash (String)
  ├── doctor_id (String)
  └── created_at (DateTime)

turns
  ├── id (UUID)
  ├── conversation_id (FK)
  ├── turn_number (Integer)
  ├── user_input (Text)
  ├── ai_response (Text)
  ├── ai_response_json (JSON)
  └── timestamp (DateTime)

findings
  ├── id (UUID)
  ├── conversation_id (FK)
  ├── turn_id (FK)
  ├── finding_type (Enum: diagnosis, drug, recommendation, lab)
  ├── value (Text)
  ├── confidence (Float: 0.0-1.0)
  ├── metadata (JSON)
  └── created_at (DateTime)

audit_logs
  ├── id (UUID)
  ├── turn_id (FK)
  ├── action (String)
  ├── details (JSON)
  └── timestamp (DateTime)
```

## Context Extraction

The service automatically extracts findings from AI responses:

### JSON Parsing
```json
{
  "diagnosis": "Migraine with fever",
  "drugs": ["Paracetamol 500mg"],
  "recommendations": ["Rest and hydration"],
  "labs": ["Blood test"]
}
```

### Text Pattern Matching
- Diagnosis: "diagnosed with", "diagnosis:", "condition"
- Drug: "prescribe", "medication", "drug"
- Lab: "lab", "test", "order lab"
- Recommendation: "recommend", "suggest", "patient should"

## Turn Linking

Automatically links findings across turns:
- **Exact Matches**: Identical or near-identical values
- **Semantic Matches**: Similar meanings (word overlap > 50%)
- **Finding Chains**: Diagnosis → Treatment, Diagnosis → Lab sequences

## Testing with curl

```bash
#!/bin/bash

# Health check
curl -X GET http://localhost:8000/health | jq .

# Start conversation
CONV_ID=$(curl -s -X POST http://localhost:8000/conversations/start \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id_hash": "patient_123",
    "doctor_id": "dr_john_001"
  }' | jq -r '.id')

echo "Created conversation: $CONV_ID"

# Add turn with JSON response
curl -s -X POST http://localhost:8000/turns/add \
  -H "Content-Type: application/json" \
  -d "{
    \"conversation_id\": \"$CONV_ID\",
    \"user_input\": \"Patient complains of headache and fever\",
    \"ai_response\": \"{\\\"diagnosis\\\": \\\"Migraine with fever\\\", \\\"drugs\\\": [\\\"Paracetamol 500mg\\\"], \\\"recommendations\\\": [\\\"Rest\\\"]}\\"
  }" | jq .

# Get all findings
curl -s -X GET http://localhost:8000/findings/$CONV_ID | jq .

# Get audit trail
curl -s -X GET http://localhost:8000/audit/conversation/$CONV_ID | jq .
```

## Finding Confidence Scores

- **JSON-extracted**: confidence = 1.0 (high confidence)
- **Text-pattern matched**: confidence = 0.7 (moderate confidence)

## Deployment

### Docker Compose
```bash
docker-compose up -d
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `PYTHONUNBUFFERED`: Set to 1 for real-time logging

### Swagger/ReDoc Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
conversation-service/
├── app.py                 # FastAPI application
├── models.py             # SQLAlchemy models
├── schemas.py            # Pydantic schemas
├── database.py           # Database setup
├── context_extractor.py  # Finding extraction
├── turn_linker.py        # Turn linking logic
├── state_manager.py      # State persistence
├── requirements.txt      # Dependencies
├── Dockerfile           # Docker image
├── docker-compose.yml   # Docker setup
├── init_db.sql          # SQL schema
└── README.md            # This file
```

## License

Part of the Althea medical platform.
# Althea
