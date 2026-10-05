# Medical AI - HIPAA-Compliant Healthcare Assistant

A customized OpenWebUI fork built with Python (FastAPI) backend and React frontend for medical AI applications. Features automatic PHI (Protected Health Information) detection, multi-agent reasoning, and comprehensive audit logging.

## Overview

Medical AI is an enterprise-grade healthcare assistant that combines:

- **FastAPI Backend**: Robust, type-safe Python backend with async support
- **React Frontend**: Modern, responsive UI with dark/light themes
- **CrewAI Integration**: Multi-agent medical reasoning system
- **PHI Detection**: Automatic identification and protection of patient data
- **Audit Logging**: Complete compliance audit trail
- **SQLAlchemy ORM**: Flexible database abstraction
- **JWT Authentication**: Secure token-based auth

## Features

### 1. PHI Detection & Protection

Automatically detects and protects:
- Patient names
- Email addresses
- Phone numbers
- SSNs and Medical Record Numbers
- Dates of birth

Modal interface allows users to review detected PHI and choose to anonymize before sending.

### 2. Multi-Agent Reasoning

Medical AI leverages CrewAI agents for specialized analysis:

- **Diagnostic Agent**: Symptom analysis and differential diagnosis
- **Evidence Agent**: Clinical evidence and medical literature review
- **Pharmacology Agent**: Medication interactions and treatment options
- **Risk Assessment Agent**: Patient risk factors and safety concerns

Each agent provides reasoning with confidence scores visible in the UI.

### 3. Conversation Management

- Create and organize conversations by date
- Sidebar navigation with collapsible design
- Previous turn context display
- Model selection per conversation
- Message history persistence

### 4. Comprehensive Audit Logging

Track all actions:
- Message sent
- PHI detected
- Data anonymized
- Model changed

Expandable audit log entries with timestamps and detailed JSON context.

### 5. Secure Architecture

- JWT token-based authentication
- Password hashing with bcrypt
- Environment-based configuration
- Secure file handling
- HIPAA-aligned data protection

## Project Structure

```
openwebui-medical/
├── backend/
│   ├── app.py                    # FastAPI main app
│   ├── auth.py                   # JWT authentication
│   ├── chat.py                   # Message handling + CrewAI routing
│   ├── phi_detector.py          # PHI detection engine
│   ├── models.py                # SQLAlchemy database models
│   ├── schemas.py               # Pydantic validation schemas
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Environment variables template
│   └── Dockerfile               # Container definition
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── PHIDetectionModal.jsx
│   │   │   ├── ContextDisplay.jsx
│   │   │   ├── AgentReasoningDisplay.jsx
│   │   │   ├── AuditLogViewer.jsx
│   │   │   ├── ModelSelector.jsx
│   │   │   └── MessageBubble.jsx
│   │   ├── App.jsx              # Main app component
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Global styles
│   ├── index.html               # HTML entry point
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── Dockerfile               # Container definition
│   └── README.md                # Frontend documentation
│
├── docker-compose.yml           # Multi-container orchestration
└── README.md                    # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### Local Development

#### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations (automatic on first run)
# Run the server
python app.py
```

The backend will be available at `http://localhost:8000`

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

#### 3. CrewAI Backend

The system expects a CrewAI backend at `http://localhost:8001`. You can:

- Run a mock backend (returns sample responses)
- Connect to your existing CrewAI deployment
- Modify `CREWAI_BACKEND_URL` in backend `.env`

### Docker Deployment

```bash
docker-compose up --build
```

Access:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs` (Swagger UI)

## Configuration

### Backend (.env)

```bash
# Database (SQLite or PostgreSQL)
DATABASE_URL=sqlite:///./medical_ai.db
# DATABASE_URL=postgresql://user:password@localhost/medical_ai

# Security - Change in production!
SECRET_KEY=your-secret-key-change-in-production

# CrewAI service URL
CREWAI_BACKEND_URL=http://localhost:8001

# Optional API Keys
ANTHROPIC_API_KEY=sk-...
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000
```

## API Documentation

### Authentication

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Patient reports chest pain",
    "model": "mistral",
    "conversation_id": 1
  }'
```

### PHI Detection

```bash
curl -X POST http://localhost:8000/phi/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "John Smith called at 555-1234"}'
```

### Full API Docs

Auto-generated Swagger UI available at:
`http://localhost:8000/docs`

## Database Schema

### Users
- Secure password storage with bcrypt
- Email-based authentication
- Activity timestamps

### Conversations
- Organized by user
- Model selection per conversation
- Creation and update timestamps

### Messages
- Full conversation history
- PHI detection metadata
- Agent reasoning details
- Anonymization tracking

### AgentReasoning
- Detailed reasoning from each agent
- Confidence scores
- Timestamp tracking

### AuditLogs
- Comprehensive action logging
- Detailed context JSON
- Full compliance trail

### FileUploads
- Support for PDF, images, CSV
- File metadata tracking
- Association with conversations

## Security Considerations

1. **PHI Protection**
   - Automatic detection of sensitive data
   - Optional anonymization before submission
   - Encrypted storage option
   - HIPAA audit compliance

2. **Authentication**
   - JWT token-based (8-hour default expiration)
   - Bcrypt password hashing
   - Secure token verification

3. **Data Isolation**
   - User-scoped conversation access
   - Database-level security
   - File upload validation

4. **Production Hardening**
   - Change `SECRET_KEY` to random 64+ char string
   - Use PostgreSQL instead of SQLite
   - Enable HTTPS/TLS
   - Configure proper CORS origins
   - Use environment variable management system
   - Regular database backups
   - Rate limiting on auth endpoints

## Development

### Backend Testing

```bash
cd backend
python -m pytest
```

### Frontend Linting

```bash
cd frontend
npm run lint
```

### Building for Production

Backend:
```bash
pip install -r requirements.txt
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

Frontend:
```bash
npm run build
# dist/ folder ready for deployment
```

## Troubleshooting

### Backend Won't Start

- Check Python version: `python --version` (need 3.11+)
- Verify dependencies: `pip install -r requirements.txt`
- Check database path in `.env`

### Frontend Not Connecting

- Verify backend is running: `http://localhost:8000/health`
- Check `VITE_API_URL` in `.env`
- Browser console for API errors

### PHI Detection Not Working

- Verify `phi_detector.py` is being imported
- Check regex patterns in `phi_detector.py`
- Test with `/phi/detect` endpoint directly

### CrewAI Integration

- Ensure CrewAI backend is running on configured URL
- Check `CREWAI_BACKEND_URL` in backend `.env`
- API returns mock data if CrewAI unavailable (safe fallback)

## Performance Tips

1. Use PostgreSQL in production (SQLite for dev only)
2. Enable database connection pooling
3. Implement caching for frequently accessed data
4. Use CDN for frontend static assets
5. Enable gzip compression on server
6. Optimize database indexes on audit logs

## Compliance

Medical AI is designed with HIPAA compliance in mind:

- ✓ Automatic PHI detection
- ✓ Comprehensive audit logging
- ✓ Secure authentication
- ✓ Data encryption support
- ✓ User access controls
- ✓ Activity tracking

*Note: Ensure proper infrastructure setup and data handling policies for full HIPAA compliance*

## Contributing

1. Follow PEP 8 (Python) and ESLint (JavaScript) standards
2. Write tests for new features
3. Document API changes in docstrings
4. Update README for user-facing changes

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
1. Check existing documentation
2. Review API docs at `/docs`
3. Check audit logs for debugging
4. Enable debug logging if needed

## Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom model fine-tuning
- [ ] Integration with EHR systems
- [ ] Telemedicine video support
- [ ] Mobile native apps
- [ ] Advanced RAG with medical literature
- [ ] Predictive analytics

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [CrewAI](https://crewai.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Vite](https://vitejs.dev/)

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready
