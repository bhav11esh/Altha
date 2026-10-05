# MediAI Platform Architecture

## System Overview

MediAI is a microservices-based medical AI platform that combines multiple specialized services to provide intelligent medical assistance through a web interface.

```
┌────────────────────────────────────────────────────────────────┐
│                    Client Layer                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │     Web Browser (React/Vite Frontend)                    │  │
│  │     - Port 3000                                          │  │
│  │     - Real-time UI updates                              │  │
│  │     - Conversational interface                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬───────────────────────────────────────────┘
                     │ HTTP/WebSocket
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                    API Layer (Nginx)                            │
│  Port 3000 & 8000                                              │
│  - Reverse proxy                                               │
│  - Load balancing                                              │
│  - Static asset serving                                        │
└────────────────────┬───────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  OpenWebUI   │ │  Backend     │ │  Services    │
│  Frontend    │ │  (Port 8000) │ │  (Ports      │
│              │ │              │ │   8001-8003) │
└──────────────┘ └──────────────┘ └──────────────┘
        │            │                    │
        └────────────┼────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                    Service Layer                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ CrewAI Service (Port 8001)                              │  │
│  │ - Agent orchestration                                   │  │
│  │ - Task execution and scheduling                         │  │
│  │ - Medical workflow automation                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Conversation Service (Port 8002)                        │  │
│  │ - Message history management                            │  │
│  │ - Context preservation                                  │  │
│  │ - User session handling                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API Integration Service (Port 8003)                     │  │
│  │ - External API management                               │  │
│  │ - FHIR compliance                                       │  │
│  │ - Data transformation                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬───────────────────────────────────────────┘
                     │
        ┌────────────┼────────────────┐
        ▼            ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ PostgreSQL   │ │    Redis     │ │   Qdrant     │
│ (Port 5432)  │ │ (Port 6379)  │ │ (Port 6333)  │
│              │ │              │ │              │
│ Relational   │ │ In-Memory    │ │ Vector DB    │
│ Database     │ │ Cache        │ │ (Embeddings) │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Component Architecture

### Frontend Layer
**Technology**: React/Vite (Node.js 18)
- Single Page Application (SPA)
- Real-time communication via WebSocket
- Responsive medical UI
- Built and served by Nginx

### Service Layer

#### 1. CrewAI Service (Python 3.11)
```
Purpose: AI Agent Framework
- Multi-agent task orchestration
- Medical reasoning workflows
- Agent state management
- Task scheduling and execution

Key Dependencies:
- crewai framework
- FastAPI
- SQLAlchemy ORM
- Redis for state management

Endpoints:
POST   /api/tasks              - Create task
GET    /api/tasks/{id}         - Get task status
GET    /api/agents             - List agents
POST   /api/agents/execute     - Execute agent workflow
```

#### 2. Conversation Service (Python 3.11)
```
Purpose: Conversation Management
- Message persistence
- Context management
- User session handling
- Conversation history

Key Dependencies:
- FastAPI
- SQLAlchemy ORM
- PostgreSQL driver
- Redis for sessions

Endpoints:
POST   /api/conversations              - Create
GET    /api/conversations              - List
GET    /api/conversations/{id}         - Get
POST   /api/conversations/{id}/messages - Add message
GET    /api/conversations/{id}/messages - Get messages
```

#### 3. API Integration Service (Python 3.11)
```
Purpose: External API Integration
- FHIR resource management
- Medical API integration (Epic, Cerner)
- Data validation and transformation
- Rate limiting and caching

Key Dependencies:
- FastAPI
- FHIR library
- requests/httpx
- SQLAlchemy ORM

Endpoints:
POST   /api/patients              - Create patient
GET    /api/patients/{id}         - Get patient data
POST   /api/fhir/validate         - Validate FHIR
GET    /api/medical-providers     - List providers
```

#### 4. OpenWebUI Backend (Python 3.11)
```
Purpose: Web Interface Backend
- Configuration serving
- API proxying
- User authentication
- Real-time notifications

Key Dependencies:
- FastAPI
- WebSockets
- python-socketio
- CORS middleware
```

### Data Layer

#### PostgreSQL (15)
```
Purpose: Primary Relational Database
- User accounts and authentication
- Conversation history
- Patient records
- Medical data storage

Key Features:
- ACID compliance
- Full-text search
- JSON support
- Row-level security

Volumes:
- postgres_data: Persistent storage
```

#### Redis (7-Alpine)
```
Purpose: In-Memory Cache & Session Store
- Session management
- Rate limiting
- Real-time caching
- Message queuing

Key Features:
- Sub-millisecond latency
- Data persistence (AOF)
- Pub/Sub messaging

Volumes:
- redis_data: Persistence
```

#### Qdrant (Latest)
```
Purpose: Vector Database
- Medical embeddings storage
- Semantic search capability
- Similar document retrieval
- AI model integration

Key Features:
- Vector similarity search
- Payload filtering
- HNSW indexing
- Snapshot capability

Volumes:
- qdrant_data: Vector storage
```

## Data Flow

### Query Flow
```
1. User submits query in UI (Port 3000)
   ↓
2. Request sent to Nginx (Port 3000/8000)
   ↓
3. OpenWebUI Backend receives request (Port 8000)
   ↓
4. Routes to API Integration Service (Port 8003)
   ↓
5. Checks Redis cache, queries PostgreSQL
   ↓
6. If needed, calls CrewAI Service (Port 8001)
   ↓
7. CrewAI processes with AI agents
   ↓
8. Results stored in PostgreSQL
   ↓
9. Embeddings stored in Qdrant
   ↓
10. Response returned through Conversation Service
    ↓
11. UI updates in real-time
```

### Conversation Flow
```
1. User initiates conversation
   ↓
2. Conversation Service creates session
   ↓
3. Messages stored in PostgreSQL
   ↓
4. CrewAI processes medical context
   ↓
5. Response generated and cached
   ↓
6. Update broadcast via WebSocket
```

## Service Dependencies

```
PostgreSQL (dependencies: none - base service)
    ↑
    ├── Used by: Conversation Service
    ├── Used by: API Integration
    ├── Used by: CrewAI
    └── Used by: OpenWebUI Backend

Redis (dependencies: none - base service)
    ↑
    ├── Used by: Conversation Service
    ├── Used by: API Integration
    └── Used by: CrewAI

Qdrant (dependencies: none - base service)
    ↑
    └── Used by: CrewAI

CrewAI (dependencies: PostgreSQL, Redis, Qdrant)
    ↑
    ├── Used by: Conversation Service
    └── Used by: API Integration

Conversation Service (dependencies: PostgreSQL, Redis, CrewAI)
    ↑
    └── Used by: API Integration

API Integration (dependencies: PostgreSQL, Conversation, CrewAI)
    ↑
    └── Used by: OpenWebUI Backend

OpenWebUI Backend (dependencies: API Integration, Conversation Service)
    ↑
    └── Used by: Frontend

Frontend (dependencies: OpenWebUI Backend)
    ↑
    └── Users interact here
```

## Environment-Specific Configurations

### Development
- Hot reload enabled
- Verbose logging (DEBUG level)
- No resource limits
- Local volume mounts
- Direct service access

### Production
- Optimized builds
- Minimal logging (WARN level)
- Resource limits enforced
- Replicated services
- Health checks active
- Automatic restarts

## Network Architecture

### Internal Communication
Services communicate via service names within Docker network:
```
crewai:8001 (internal)
conversation-service:8002 (internal)
api-integration:8003 (internal)
postgres:5432 (internal)
redis:6379 (internal)
qdrant:6333 (internal)
```

### External Ports
```
3000  - Frontend
8000  - Backend API
8001  - CrewAI (optional external)
8002  - Conversation (optional external)
8003  - API Integration
5432  - PostgreSQL (optional external)
6379  - Redis (optional external)
6333  - Qdrant (optional external)
```

## Security Architecture

### Network Security
- Services isolated on custom bridge network
- No external exposure unless configured
- Firewall rules per environment
- TLS/SSL for external connections

### Data Security
- PostgreSQL with strong credentials
- Redis password protection
- Qdrant API key authentication
- Secrets managed via environment variables

### Application Security
- CORS middleware configured
- Rate limiting via API Integration
- Input validation on all endpoints
- Authentication/Authorization support ready

## Scalability Design

### Horizontal Scaling
- Stateless services allow replication
- Load balancer (Nginx) distributes traffic
- Shared database backend
- Redis for distributed sessions

### Vertical Scaling
- Resource limits per service
- Container memory management
- CPU allocation strategies
- Priority-based scheduling

## Monitoring & Observability

### Health Checks
Each service exposes `/health` endpoint:
```
GET /health → {status: "healthy", timestamp, service}
```

### Logging
- Structured JSON logging
- Centralized log collection ready
- Log level configuration per environment
- Request/response logging

### Metrics
- Docker stats available
- Service performance monitoring
- Database query logging
- API response time tracking

## Technology Stack Summary

| Layer | Technology | Version | Port |
|-------|-----------|---------|------|
| Frontend | React/Vite | 18.2/5.0 | 3000 |
| Web Server | Nginx | Latest | 3000/8000 |
| CrewAI | Python/FastAPI | 3.11 | 8001 |
| Conversation | Python/FastAPI | 3.11 | 8002 |
| API Integration | Python/FastAPI | 3.11 | 8003 |
| OpenWebUI Backend | Python/FastAPI | 3.11 | 8000 |
| Database | PostgreSQL | 15 | 5432 |
| Cache | Redis | 7-Alpine | 6379 |
| Vector DB | Qdrant | Latest | 6333 |
| Container Runtime | Docker | 20.10+ | - |
| Orchestration | Docker Compose | 1.29+ | - |
