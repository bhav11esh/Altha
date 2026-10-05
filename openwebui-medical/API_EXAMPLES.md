# Medical AI API Examples

Complete curl examples for testing the Medical AI backend.

## Base URL

```
http://localhost:8000
```

## Interactive API Documentation

Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

## Authentication

### Register New User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "id": 1,
  "email": "doctor@example.com",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the token for subsequent requests:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Get Current User

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Conversations

### Create Conversation

```bash
curl -X POST http://localhost:8000/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Patient John Doe - Initial Assessment",
    "model": "mistral"
  }'
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Patient John Doe - Initial Assessment",
  "model": "mistral",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "messages": []
}
```

### List All Conversations

```bash
curl -X GET http://localhost:8000/conversations \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
[
  {
    "id": 1,
    "title": "Patient John Doe - Initial Assessment",
    "model": "mistral",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:35:00",
    "message_count": 3
  }
]
```

### Get Single Conversation

```bash
curl -X GET http://localhost:8000/conversations/1 \
  -H "Authorization: Bearer $TOKEN"
```

## Chat & Messages

### Send Message (Creates new conversation if needed)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Patient reports persistent headache, worse with light exposure, accompanied by nausea",
    "model": "mistral",
    "conversation_id": 1,
    "include_context": true,
    "context_limit": 2
  }'
```

Response:
```json
{
  "id": 2,
  "conversation_id": 1,
  "role": "assistant",
  "content": "Based on the symptoms you've described...",
  "detected_phi": null,
  "is_anonymized": false,
  "model_used": "mistral",
  "agent_reasoning": [
    {
      "agent_name": "Diagnostic",
      "reasoning_text": "Initial assessment suggests possible migraine or meningitis",
      "confidence_score": 85
    },
    {
      "agent_name": "Evidence",
      "reasoning_text": "Photophobia and nausea are strong indicators of migraine",
      "confidence_score": 78
    }
  ],
  "created_at": "2024-01-15T10:35:00"
}
```

## PHI Detection

### Detect PHI in Text

```bash
curl -X POST http://localhost:8000/phi/detect \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient John Smith, DOB: 05/15/1985, SSN: 123-45-6789, email: john@example.com, phone: 555-123-4567"
  }'
```

Response:
```json
{
  "text": "Patient John Smith, DOB: 05/15/1985, SSN: 123-45-6789, email: john@example.com, phone: 555-123-4567",
  "phi": {
    "names": ["John Smith"],
    "ids": ["123-45-6789"],
    "emails": ["john@example.com"],
    "phones": ["555-123-4567"],
    "medical_records": []
  },
  "has_phi": true
}
```

### Preview Anonymization

```bash
curl -X GET http://localhost:8000/phi/preview \
  -H "Content-Type: application/json" \
  --data-urlencode "text=Patient John Smith, SSN: 123-45-6789, called at 555-123-4567"
```

Response:
```json
{
  "original": "Patient John Smith, SSN: 123-45-6789, called at 555-123-4567",
  "anonymized": "Patient [PATIENT_0], SSN: [SSN_1], called at [PHONE_2]",
  "replacements": {
    "John Smith": "[PATIENT_0]",
    "123-45-6789": "[SSN_1]",
    "555-123-4567": "[PHONE_2]"
  },
  "phi_count": 3
}
```

### Anonymize Message

```bash
curl -X POST "http://localhost:8000/phi/anonymize?message_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "message_id": 1,
  "anonymized_content": "Patient [PATIENT_0] reports [MEDICAL_0]...",
  "replacements": {
    "John Smith": "[PATIENT_0]",
    "chest pain": "[MEDICAL_0]"
  }
}
```

## Audit Logs

### Get User's Audit Log

```bash
curl -X GET "http://localhost:8000/audit-logs?limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "action": "message_sent",
    "details": {
      "conversation_id": 1,
      "message_id": 2,
      "model": "mistral",
      "has_phi": false
    },
    "timestamp": "2024-01-15T10:35:00"
  },
  {
    "id": 2,
    "user_id": 1,
    "action": "phi_detected",
    "details": {
      "message_id": 1,
      "phi_types": {
        "names": 1,
        "ids": 1,
        "emails": 1,
        "phones": 1,
        "medical_records": 0
      }
    },
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

## Context

### Get Previous Context from Conversation

```bash
curl -X GET "http://localhost:8000/conversations/1/context?turn_limit=2" \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "context": [
    {
      "id": 1,
      "conversation_id": 1,
      "role": "user",
      "content": "Patient reports fever and cough",
      "created_at": "2024-01-15T10:20:00"
    },
    {
      "id": 2,
      "conversation_id": 1,
      "role": "assistant",
      "content": "Possible respiratory infection...",
      "created_at": "2024-01-15T10:25:00"
    }
  ]
}
```

## File Upload

### Upload File to Conversation

```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/patient_report.pdf" \
  -F "conversation_id=1"
```

Response:
```json
{
  "id": 1,
  "conversation_id": 1,
  "filename": "patient_report.pdf",
  "file_type": "pdf",
  "size_bytes": 245632,
  "created_at": "2024-01-15T10:40:00"
}
```

Supported file types:
- PDF: `application/pdf`
- Images: `image/jpeg`, `image/png`
- CSV: `text/csv`

## Health Check

### Service Health

```bash
curl -X GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy"
}
```

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found

```json
{
  "detail": "Conversation not found"
}
```

### 400 Bad Request

```json
{
  "detail": "Email already registered"
}
```

### 413 Payload Too Large

```json
{
  "detail": "File too large (max 10MB)"
}
```

## Sample Workflow

```bash
# 1. Register
TOKEN=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

# 2. Login (if already registered)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' | jq -r '.access_token')

# 3. Create conversation
CONV=$(curl -s -X POST http://localhost:8000/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Patient Assessment", "model": "mistral"}')

CONV_ID=$(echo $CONV | jq -r '.id')

# 4. Send message
curl -s -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"Patient reports chest pain\",
    \"model\": \"mistral\",
    \"conversation_id\": $CONV_ID
  }"

# 5. View audit logs
curl -s -X GET http://localhost:8000/audit-logs \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

## Advanced Examples

### Multi-turn Conversation with Context

```bash
# Message 1
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Patient has high fever for 3 days",
    "model": "mistral",
    "conversation_id": 1
  }'

# Message 2 (with context from previous turn)
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What medications would you recommend?",
    "model": "mistral",
    "conversation_id": 1,
    "include_context": true,
    "context_limit": 2
  }'
```

### Testing with different models

```bash
for model in mistral llama gpt-4o; do
  curl -X POST http://localhost:8000/chat \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"content\": \"Test message\",
      \"model\": \"$model\",
      \"conversation_id\": 1
    }"
done
```

## Rate Limiting

Currently no rate limiting is implemented in the demo. In production, implement:
- Per-user request limits
- Per-IP address limits
- Exponential backoff for auth endpoints

## CORS

The API accepts requests from:
- `http://localhost:3000`
- `http://localhost:5173`

Configure additional origins in `app.py` as needed.

---

For more details, see the main README.md or check the auto-generated Swagger docs.
