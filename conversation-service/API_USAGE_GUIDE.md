# Conversation Service API Usage Guide

## Quick Reference

### Base URL
```
http://localhost:8000
```

### Authentication
Currently no authentication (add custom auth as needed)

### Response Format
All responses are JSON with appropriate HTTP status codes.

## Endpoints Reference

### Health Check
```
GET /health
```
Returns: `{"status": "healthy", "service": "conversation-service"}`

### 1. Start a Conversation
```
POST /conversations/start
Content-Type: application/json

{
  "patient_id_hash": "string - hashed patient identifier",
  "doctor_id": "string - doctor identifier"
}
```

**Success Response (201)**:
```json
{
  "id": "uuid",
  "patient_id_hash": "string",
  "doctor_id": "string",
  "created_at": "2024-10-04T10:00:00"
}
```

### 2. Add a Turn
```
POST /turns/add
Content-Type: application/json

{
  "conversation_id": "uuid - from start_conversation response",
  "user_input": "string - patient/user input",
  "ai_response": "string or JSON string - AI response with findings"
}
```

**Success Response (201)**:
```json
{
  "turn_id": "uuid",
  "conversation_id": "uuid",
  "turn_number": 1,
  "timestamp": "2024-10-04T10:05:00",
  "findings_extracted": [
    {
      "id": "uuid",
      "conversation_id": "uuid",
      "turn_id": "uuid",
      "finding_type": "diagnosis|drug|recommendation|lab",
      "value": "string",
      "confidence": 0.0-1.0,
      "metadata": null,
      "created_at": "2024-10-04T10:05:00"
    }
  ],
  "context_linked": false
}
```

### 3. Get All Turns
```
GET /turns/{conversation_id}
```

**Response (200)**:
```json
[
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "turn_number": 1,
    "user_input": "string",
    "ai_response": "string",
    "timestamp": "2024-10-04T10:05:00",
    "findings": [...],
    "audit_logs": [...]
  }
]
```

### 4. Get Enriched Context for a Turn
```
GET /context/{turn_id}?conversation_id={conversation_id}
```

**Response (200)**:
```json
{
  "conversation_id": "uuid",
  "turn_id": "uuid",
  "context": {
    "turn_id": "uuid",
    "turn_number": 1,
    "timestamp": "2024-10-04T10:05:00",
    "current_findings": [
      {
        "id": "uuid",
        "type": "diagnosis",
        "value": "string",
        "confidence": 0.0-1.0
      }
    ],
    "previous_findings": [
      {
        "id": "uuid",
        "type": "string",
        "value": "string",
        "confidence": 0.0-1.0,
        "from_turn": 1
      }
    ],
    "related_findings": {
      "exact_matches": [],
      "semantic_matches": []
    },
    "conversation_context": {
      "previous_findings_count": 0,
      "by_type": {
        "diagnosis": [],
        "drug": [],
        "lab": [],
        "recommendation": []
      },
      "timeline": []
    }
  }
}
```

### 5. Get All Findings
```
GET /findings/{conversation_id}?finding_type=diagnosis
```

**Query Parameters**:
- `finding_type` (optional): Filter by type (diagnosis, drug, recommendation, lab)

**Response (200)**:
```json
{
  "conversation_id": "uuid",
  "findings": [],
  "total_findings": 4,
  "by_type": {
    "diagnosis": 1,
    "drug": 1,
    "recommendation": 1,
    "lab": 1
  }
}
```

### 6. Get Audit Log for a Turn
```
GET /audit/{turn_id}
```

**Response (200)**:
```json
[
  {
    "id": "uuid",
    "turn_id": "uuid",
    "action": "findings_extracted|turn_created",
    "details": {
      "count": 4,
      "types": ["diagnosis", "drug", "recommendation", "lab"]
    },
    "timestamp": "2024-10-04T10:05:00"
  }
]
```

### 7. Get Conversation Audit Trail
```
GET /audit/conversation/{conversation_id}
```

**Response (200)**:
```json
{
  "conversation_id": "uuid",
  "total_entries": 2,
  "audit_logs": [
    {
      "id": "uuid",
      "turn_number": 1,
      "action": "findings_extracted",
      "details": {...},
      "timestamp": "2024-10-04T10:05:00"
    }
  ]
}
```

### 8. Get Context Chains
```
GET /context-chains/{conversation_id}
```

**Response (200)**:
```json
{
  "conversation_id": "uuid",
  "chains": {
    "diagnosis_to_treatment": [
      {
        "diagnosis": "string",
        "diagnosis_turn": 1,
        "treatment": "string",
        "treatment_turn": 2,
        "gap_turns": 1
      }
    ],
    "diagnosis_to_lab": [],
    "lab_to_diagnosis": [],
    "all_findings_timeline": []
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Conversation not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

## Common Usage Patterns

### Pattern 1: Create Conversation and Add Turns
```python
import requests

API = "http://localhost:8000"

# Start conversation
conv = requests.post(f"{API}/conversations/start", json={
    "patient_id_hash": "patient_123",
    "doctor_id": "dr_001"
}).json()
conv_id = conv['id']

# Add first turn
turn1 = requests.post(f"{API}/turns/add", json={
    "conversation_id": conv_id,
    "user_input": "Patient reports fever",
    "ai_response": '{"diagnosis": "Fever", "drugs": ["Paracetamol"]}'
}).json()

# Add second turn
turn2 = requests.post(f"{API}/turns/add", json={
    "conversation_id": conv_id,
    "user_input": "Fever reduced",
    "ai_response": "Diagnosis improving. Continue medication."
}).json()
```

### Pattern 2: Get Enriched Context
```python
import requests

API = "http://localhost:8000"

# Get enriched context for latest turn
context = requests.get(
    f"{API}/context/{turn_id}",
    params={"conversation_id": conv_id}
).json()

# Access previous findings
previous = context['context']['previous_findings']
related = context['context']['related_findings']
```

### Pattern 3: Analyze Findings
```python
import requests

API = "http://localhost:8000"

# Get all findings
findings = requests.get(f"{API}/findings/{conv_id}").json()

# Get findings by type
diagnoses = requests.get(
    f"{API}/findings/{conv_id}",
    params={"finding_type": "diagnosis"}
).json()

# Get finding chains
chains = requests.get(f"{API}/context-chains/{conv_id}").json()

# Analyze diagnosis to treatment flow
for chain in chains['chains']['diagnosis_to_treatment']:
    print(f"{chain['diagnosis']} -> {chain['treatment']} in {chain['gap_turns']} turns")
```

### Pattern 4: Audit Trail Review
```python
import requests

API = "http://localhost:8000"

# Get complete audit trail
audit = requests.get(f"{API}/audit/conversation/{conv_id}").json()

# Track all actions
for entry in audit['audit_logs']:
    print(f"Turn {entry['turn_number']}: {entry['action']}")
```

## AI Response Formats

### Format 1: Structured JSON
```python
ai_response = json.dumps({
    "diagnosis": "Migraine with fever",
    "drugs": [
        "Paracetamol 500mg",
        "Ibuprofen 200mg"
    ],
    "recommendations": [
        "Rest",
        "Hydration"
    ],
    "labs": [
        "Blood test",
        "CT scan"
    ]
})
```

### Format 2: Natural Language
```python
ai_response = """
Patient presents with persistent headache. Diagnosis: Chronic migraine.
Prescribed: Sumatriptan 100mg. Recommended: Rest, avoid triggers.
Order lab tests: MRI brain.
"""
```

### Format 3: Mixed Format
```python
ai_response = """
Assessment: The patient shows signs of upper respiratory infection.

Diagnosis: Acute pharyngitis
Medications: Amoxicillin 500mg three times daily
Recommendations: Rest, warm liquids, throat lozenges
Tests: Throat swab for culture
"""
```

## Best Practices

### 1. Patient ID Hashing
Always hash patient IDs before sending:
```python
import hashlib

patient_id = "12345"
hashed = hashlib.sha256(patient_id.encode()).hexdigest()
```

### 2. Structured JSON Responses
Use structured JSON format for better extraction:
```python
# Good
ai_response = json.dumps({
    "diagnosis": "...",
    "drugs": [...]
})

# Less optimal (but still works)
ai_response = "Diagnosis: ... Prescribe: ..."
```

### 3. Error Handling
```python
import requests

try:
    response = requests.post(f"{API}/turns/add", json=data)
    response.raise_for_status()
    turn = response.json()
except requests.exceptions.HTTPError as e:
    if response.status_code == 404:
        print("Conversation not found")
    elif response.status_code == 400:
        print("Invalid input")
    else:
        print(f"Server error: {e}")
```

### 4. Rate Limiting
For production use, implement rate limiting:
```python
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=2, max=10))
def add_turn_with_retry(api, data):
    return requests.post(f"{api}/turns/add", json=data)
```

## Integration Tips

### With Langchain/LLM
```python
from conversation_service import ConversationClient

client = ConversationClient("http://localhost:8000")

# Start conversation
conv_id = client.start_conversation(
    patient_id_hash=hash_patient_id(patient_id),
    doctor_id=doctor_id
)

# Add turns from LLM chain
for llm_response in llm_chain.stream(...):
    turn = client.add_turn(
        conversation_id=conv_id,
        user_input=user_query,
        ai_response=json.dumps(llm_response)
    )
    
    # Get context for next turn
    context = client.get_enriched_context(turn['turn_id'], conv_id)
```

## Performance Considerations

- Typical latency per turn: 50-200ms
- JSON extraction: ~10ms
- Text pattern matching: ~20ms
- Database write: ~50ms
- Context enrichment: ~100ms

For high volume:
- Use connection pooling
- Batch related requests
- Cache frequently accessed conversations
- Implement pagination for large result sets
