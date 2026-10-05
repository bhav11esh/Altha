# Development Guide - Medical AI

Complete guide for developers working on Medical AI.

## Getting Started

### Clone and Setup

```bash
git clone <repo>
cd openwebui-medical

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
cp .env.example .env

# Frontend setup
cd ../frontend
npm install
```

### Start Development Servers

**Option 1: Using the startup script**
```bash
chmod +x start.sh
./start.sh
```

**Option 2: Manual (two terminals)**

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
python app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

## Architecture

### Backend Architecture

```
FastAPI (app.py)
├── Auth (auth.py)
│   ├── JWT token generation
│   ├── Password hashing
│   └── User authentication
│
├── Database (models.py, SQLAlchemy)
│   ├── Users
│   ├── Conversations
│   ├── Messages
│   └── AuditLogs
│
├── PHI Detection (phi_detector.py)
│   ├── Pattern matching
│   ├── Anonymization
│   └── Storage
│
├── Chat Logic (chat.py)
│   ├── Message processing
│   ├── CrewAI integration
│   └── Agent reasoning
│
└── API Endpoints
    ├── /auth/* (authentication)
    ├── /conversations/* (conversation management)
    ├── /chat (message handling)
    ├── /phi/* (PHI detection)
    ├── /audit-logs (audit trail)
    └── /files/upload (file uploads)
```

### Frontend Architecture

```
React App (App.jsx)
├── Authentication
│   ├── Login/Register
│   └── Token management
│
├── Layout
│   ├── Sidebar (conversations)
│   ├── Header (model selector)
│   └── Main content area
│
└── Components
    ├── ChatInterface (main chat UI)
    ├── PHIDetectionModal (PHI warning)
    ├── MessageBubble (message display)
    ├── AgentReasoningDisplay (multi-agent pills)
    ├── ContextDisplay (previous turns)
    ├── AuditLogViewer (action history)
    ├── ModelSelector (model dropdown)
    └── [Support components]
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Conversations Table

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
    title VARCHAR NOT NULL,
    model VARCHAR DEFAULT 'mistral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Messages Table

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER FOREIGN KEY,
    role VARCHAR NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    detected_phi JSON,  -- PHI data found
    is_anonymized BOOLEAN DEFAULT FALSE,
    original_content TEXT,  -- backup before anonymization
    model_used VARCHAR,
    agent_reasoning JSON,  -- multi-agent reasoning
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### AuditLogs Table

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
    action VARCHAR NOT NULL,  -- 'message_sent', 'phi_detected', etc.
    details JSON,  -- action context
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Sample Data for Testing

### Test User

```json
{
    "email": "doctor@example.com",
    "password": "TestPassword123!"
}
```

### Sample Medical Query

```
Patient John Smith, DOB: 03/15/1978, reports persistent headache for 2 weeks.
Associated symptoms: sensitivity to light, mild fever (101°F), nausea.
Patient ID: MRN-123456
Contact: john.smith@email.com, 555-987-6543
```

### Sample API Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Patient reports high fever and difficulty breathing. Temperature: 103.5F, Respiratory rate: 28/min",
    "model": "mistral",
    "conversation_id": 1
  }'
```

## Development Workflow

### Adding a New Endpoint

1. **Create the endpoint in `app.py`**:

```python
@app.get("/api/example/{id}")
async def get_example(
    id: int,
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get example by ID"""
    user = db.query(User).filter(User.email == email).first()
    # Implementation here
    return {"id": id, "data": "example"}
```

2. **Add a Pydantic schema in `schemas.py`**:

```python
class ExampleResponse(BaseModel):
    id: int
    data: str
    
    class Config:
        from_attributes = True
```

3. **Add a test in frontend**:

```javascript
const response = await axios.get(
    `${API_BASE}/api/example/1`,
    { headers: { Authorization: `Bearer ${token}` } }
);
```

### Adding a New React Component

1. **Create component file**:

```jsx
// src/components/NewComponent.jsx
import React from 'react';

const NewComponent = ({ prop1, prop2 }) => {
  return (
    <div className="component">
      {/* Component JSX */}
    </div>
  );
};

export default NewComponent;
```

2. **Add to parent component**:

```jsx
import NewComponent from './components/NewComponent';

// Inside render
<NewComponent prop1="value1" prop2="value2" />
```

3. **Style with CSS Custom Properties**:

```css
.component {
  background-color: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}
```

## Testing

### Backend Testing

```bash
cd backend

# Run tests (if pytest installed)
pytest

# Test specific endpoint
curl -X GET http://localhost:8000/health

# Interactive testing
python -i app.py
>>> from models import User
>>> user = User(email="test@test.com", hashed_password="hash")
```

### Frontend Testing

```bash
cd frontend

# Run linter
npm run lint

# Build check
npm run build

# Browser DevTools (F12)
# Check:
# - Network tab for API calls
# - Console for errors
# - Application tab for localStorage
```

## API Response Patterns

### Success Response

```json
{
  "id": 1,
  "conversation_id": 1,
  "role": "assistant",
  "content": "Response text...",
  "model_used": "mistral",
  "agent_reasoning": [
    {
      "agent_name": "Diagnostic",
      "reasoning_text": "...",
      "confidence_score": 85
    }
  ],
  "created_at": "2024-01-15T10:30:00"
}
```

### Error Response

```json
{
  "detail": "Error message explaining what went wrong"
}
```

### PHI Detection Response

```json
{
  "text": "Original text...",
  "phi": {
    "names": ["John Smith"],
    "ids": ["123-45-6789"],
    "emails": ["john@example.com"],
    "phones": ["555-1234567"],
    "medical_records": ["MRN-12345"]
  },
  "has_phi": true
}
```

## Common Tasks

### Clear Database

```bash
cd backend

# SQLite
rm medical_ai.db

# PostgreSQL
psql medical_ai -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Reinitialize
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

### Add a New Database Model

1. **Define in `models.py`**:

```python
class NewModel(Base):
    __tablename__ = "new_model"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
```

2. **Create migration** (for PostgreSQL):

```bash
# Using Alembic would be ideal, but for dev:
# Just delete and reinit the database
```

3. **Add Pydantic schema in `schemas.py`**

4. **Add CRUD operations in `app.py`**

### Add New PHI Pattern

Edit `phi_detector.py`:

```python
def detect_phi(self, text: str) -> PHIDetection:
    # ... existing code ...
    
    # Add new pattern
    new_pattern = r'your-regex-here'
    matches = re.findall(new_pattern, text)
    phi.new_type = list(set(matches))
    
    return phi
```

## Debugging

### Backend Debugging

1. **Enable debug logging**:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

2. **Use Python debugger**:

```python
import pdb; pdb.set_trace()  # Will pause execution
```

3. **Check database**:

```bash
cd backend
sqlite3 medical_ai.db
> SELECT * FROM conversations;
> SELECT * FROM audit_logs;
```

### Frontend Debugging

1. **Browser DevTools** (F12):
   - Network tab: Check API requests/responses
   - Console: JavaScript errors
   - Storage: localStorage tokens
   - React DevTools: Component hierarchy

2. **Add console logs**:

```javascript
console.log('Debug:', variable);
console.error('Error:', error);
```

3. **Network inspection**:

```javascript
// In component
useEffect(() => {
  console.log('Mounted:', { conversationId, model });
  return () => console.log('Unmounted');
}, [conversationId, model]);
```

## Performance Tips

### Backend

- Use database indexes on frequently queried fields
- Implement caching with Redis
- Use async/await for I/O operations
- Lazy load relationships in SQLAlchemy
- Paginate large result sets

### Frontend

- Code splitting with dynamic imports
- Lazy load components with `React.lazy()`
- Memoize expensive computations
- Virtualize long lists
- Optimize images

## Code Style

### Python (Backend)

Follow PEP 8:

```python
def calculate_total(items: list[int]) -> int:
    """Calculate total of items.
    
    Args:
        items: List of integers
        
    Returns:
        Sum of all items
    """
    return sum(items)
```

### JavaScript (Frontend)

Follow ESLint rules:

```javascript
// Good
const calculateTotal = (items) => {
  return items.reduce((sum, item) => sum + item, 0);
};

// Bad - avoid var, use descriptive names
var total = 0;
for (let i = 0; i < items.length; i++) {
  total += items[i];
}
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add .
git commit -m "feat: description of changes"

# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Production Checklist

Before deploying:

- [ ] Change `SECRET_KEY`
- [ ] Set `DATABASE_URL` to PostgreSQL
- [ ] Enable HTTPS
- [ ] Configure CORS origins
- [ ] Set up monitoring
- [ ] Enable audit logging
- [ ] Configure backups
- [ ] Set environment variables
- [ ] Test all endpoints
- [ ] Security audit

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [SQLAlchemy Docs](https://www.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Vite Docs](https://vitejs.dev/)

---

**Version**: 1.0.0  
**Last Updated**: 2024
