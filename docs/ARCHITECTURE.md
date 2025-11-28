# Architecture Documentation

## High-Level Design

### System Overview

The PCTE AI Help Desk is a production-ready, AI-powered support system that uses Retrieval Augmented Generation (RAG) to provide accurate, KB-grounded responses while maintaining strict security guardrails.

**Key Characteristics:**
- **Deterministic tier classification** (no AI randomness)
- **KB-only responses** (no hallucinations)
- **Conversation context** (session-based memory)
- **Advanced security** (9 guardrail categories)
- **Full data persistence** (PostgreSQL + pgvector)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Chat UI      │  │ Analytics    │  │ Ticket       │         │
│  │ Component    │  │ Dashboard    │  │ Management   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         └──────────────────┴──────────────────┘                 │
│                            │                                    │
│                     API Client Layer                            │
└────────────────────────────┼───────────────────────────────────┘
                             │ REST API (JSON)
┌────────────────────────────┼───────────────────────────────────┐
│                   BACKEND (FastAPI)                             │
│                            │                                    │
│         ┌──────────────────┴──────────────────┐                │
│         │        API Layer (Endpoints)         │                │
│         │    /chat  /tickets  /metrics         │                │
│         └──────────────────┬──────────────────┘                │
│                            │                                    │
│         ┌──────────────────┴──────────────────────┐            │
│         │         Business Logic Layer            │            │
│         │                                          │            │
│    ┌────┴─────┐  ┌──────────┐  ┌─────────────┐   │            │
│    │ Guardrail│  │   RAG    │  │   Tier      │   │            │
│    │ Engine   │  │ Service  │  │ Classifier  │   │            │
│    └────┬─────┘  └────┬─────┘  └─────┬───────┘   │            │
│         │             │               │           │            │
│         │   ┌─────────┴───────┐       │           │            │
│         │   │                 │       │           │            │
│    ┌────┴───┴──┐      ┌───────┴───────┴─────┐    │            │
│    │   LLM     │      │   Vector Store      │    │            │
│    │ Provider  │      │   (pgvector)        │    │            │
│    │ (OpenAI)  │      │                     │    │            │
│    └───────────┘      └─────────────────────┘    │            │
│                                                   │            │
│         └───────────────────────────────────────┘             │
│                            │                                   │
│         ┌──────────────────┴──────────────────┐               │
│         │      Data/Repository Layer          │               │
│         │   ORM Models + Pydantic Schemas     │               │
│         └──────────────────┬──────────────────┘               │
└────────────────────────────┼──────────────────────────────────┘
                             │ SQL + Vector Queries
┌────────────────────────────┼──────────────────────────────────┐
│               PostgreSQL 16 + pgvector                          │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐            │
│  │ documents  │  │conversations │  │  messages   │            │
│  │ (vectors)  │  │              │  │             │            │
│  └────────────┘  └──────────────┘  └─────────────┘            │
│  ┌────────────┐                                                │
│  │  tickets   │                                                │
│  └────────────┘                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Frontend Layer (React)

**Purpose:** User interface and interaction

**Components:**
- `AIChatPanel` - Main chat interface with message history
- `ChatMessage` - Individual message rendering (supports markdown, chips)
- `AnalyticsDashboard` - Real-time metrics visualization
- `TicketDashboard` - Ticket management UI

**Responsibilities:**
- Render UI components
- Handle user input
- Display AI responses with metadata (confidence, tier, sources)
- Fetch data from backend APIs
- Manage local state (conversation history)

**Communication:**
- REST API calls to backend (`/api/v1/chat`, `/api/v1/metrics`, `/api/v1/tickets`)
- Sends conversation history with each request for context

---

### 2. API Layer (FastAPI Endpoints)

**Purpose:** HTTP request/response handling

**Location:** `backend/app/api/endpoints/`

**Endpoints:**
- `POST /api/v1/chat/` - Main chat endpoint
- `POST /api/v1/tickets/` - Create tickets
- `GET /api/v1/tickets/` - List tickets
- `GET /api/v1/metrics/summary` - Analytics summary
- `GET /api/v1/metrics/trends` - Time-series data

**Responsibilities:**
- Request validation (Pydantic schemas)
- Route to appropriate services
- Format responses
- Error handling

**Key Feature:**
- **No business logic** - delegates to service layer

---

### 3. Business Logic Layer

**Purpose:** Core application logic and orchestration

#### 3a. Guardrail Engine

**Location:** `backend/app/services/guardrails/`

**Purpose:** Security policy enforcement

**Features:**
- 9 pattern categories (injection, jailbreak, social engineering)
- Pattern-based detection (no LLM)
- Base64 decoding for hidden commands
- Unicode normalization
- Semantic analysis for complex attacks

**Flow:**
```
User Message → Pattern Check → Violations? → Block/Allow
```

#### 3b. RAG Service

**Location:** `backend/app/services/rag/`

**Purpose:** Retrieve relevant KB chunks and generate responses

**Components:**
- `RAGService` - Orchestrates retrieval + generation
- `VectorStore` - Interface for vector search
- `PgVectorStore` - PostgreSQL implementation
- `LocalVectorStore` - FAISS implementation (dev)

**Flow:**
```
Query → Embed → Vector Search → Top-K KB Chunks → 
LLM (with chunks) → Grounded Response
```

**Key Features:**
- Only uses retrieved KB chunks
- Cites sources
- Returns confidence scores
- Manages context window (8000 tokens)

#### 3c. Tier Classifier

**Location:** `backend/app/services/routing/tier_classifier.py`

**Purpose:** Deterministic issue classification

**Method:** Pattern-based keyword matching (NO LLM)

**4 Tiers:**
- Tier 0: Self-service (password reset, MFA)
- Tier 1: Common issues (VPN, connectivity)
- Tier 2: Infrastructure (Docker, VM crashes)
- Tier 3: Critical (kernel panic, security breach, data loss)

**Key Feature:**
- **100% deterministic** - same input → same tier (verified by unit test)

#### 3d. Analytics Tracker

**Location:** `backend/app/services/analytics/tracker.py`

**Purpose:** Track conversations, messages, and metrics

**Tracks:**
- Conversation start/end
- Message exchanges
- Tier distribution
- Confidence scores
- Ticket creation

---

### 4. LLM Abstraction Layer

**Purpose:** Provider-agnostic interface for language models

**Location:** `backend/app/services/llm/`

**Components:**
- `LLMProvider` (ABC) - Abstract interface
- `OpenAIProvider` - OpenAI implementation
- `MockLLMProvider` - Testing/fallback

**Interface:**
```python
class LLMProvider(ABC):
    async def generate_answer(prompt, context, history) -> str
    async def get_embeddings(texts) -> List[List[float]]
```

**Benefits:**
- **Swappable providers** (easy to add Anthropic, Azure OpenAI, etc.)
- **Testability** (use MockProvider in tests)
- **Configuration** (temperature, model selection centralized)

---

### 5. Data/Repository Layer

**Purpose:** Data persistence and retrieval

**Location:** `backend/app/models/`

**Components:**
- `models.py` - SQLAlchemy ORM models
- `schemas.py` - Pydantic request/response schemas

**ORM Models:**
```python
Document        # KB documents with embeddings (vector column)
Conversation    # Chat sessions
Message         # Individual messages
Ticket          # Support tickets
```

**Key Features:**
- Async operations (SQLAlchemy + asyncpg)
- pgvector extension for similarity search
- Relationships (Conversation ↔ Messages ↔ Tickets)

---

### 6. Database (PostgreSQL + pgvector)

**Purpose:** Persistent storage with vector search

**Extensions:**
- `pgvector` - Vector similarity search

**Tables:**
- `documents` - KB with embeddings (1536 dimensions)
- `conversations` - Session tracking
- `messages` - Chat history
- `tickets` - Support tickets

**Indexes:**
- Cosine similarity index on document embeddings
- B-tree indexes on session_id, conversation_id

---

## Data Flow Diagrams

### Chat Request Flow

```
1. User Input
   ↓
2. Frontend → POST /api/v1/chat
   {message, session_id, history}
   ↓
3. API Layer → Save user message to DB
   ↓
4. Guardrail Check
   ↓ [SAFE]
5. Tier Classification (pattern-based)
   ↓
6. RAG Service
   ├→ Embed query (OpenAI)
   ├→ Vector search (pgvector)
   ├→ Retrieve top-3 KB chunks
   └→ LLM generation (with chunks + history)
   ↓
7. Save assistant message to DB
   ↓
8. Return response
   {response, sources, confidence, tier, severity}
   ↓
9. Frontend displays with chips/badges
```

### Knowledge Base Ingestion Flow

```
1. KB Documents (markdown files in data/kb/)
   ↓
2. Ingestion Script (app/scripts/ingest.py)
   ├→ Read all .md files
   ├→ Chunk documents (by paragraph/section)
   ├→ Generate embeddings (OpenAI)
   └→ Store in PostgreSQL
       └→ documents table (id, text, embedding, metadata)
   ↓
3. Vector Index Created (pgvector)
   ↓
4. Ready for similarity search
```

### Analytics Data Flow

```
1. Every chat interaction
   ↓
2. Analytics Tracker
   ├→ Conversation tracking
   ├→ Message logging (with confidence, tier)
   ├→ Tier distribution aggregation
   └→ Ticket creation events
   ↓
3. PostgreSQL (conversations, messages, tickets tables)
   ↓
4. Metrics Endpoints
   ├→ /metrics/summary (aggregates)
   └→ /metrics/trends (time-series)
   ↓
5. Frontend Dashboard (real-time charts)
```

---

## Security Architecture

### Multi-Layer Security

**Layer 1: Guardrail Patterns**
- Blocks before LLM processing
- 9 categories of attacks
- Pattern matching + semantic analysis

**Layer 2: System Prompt Constraints**
```python
"ONLY use information from KB chunks"
"NEVER make up commands, procedures, URLs"
```

**Layer 3: Low Temperature**
- `temperature=0.1` minimizes hallucinations

**Layer 4: Source Tracking**
- All KB references verified
- Metadata includes actual document info

**Layer 5: Confidence Scoring**
- Low confidence when KB insufficient
- Triggers clarifying questions or escalation

---

## Scalability Considerations

### Current Architecture
- **Async operations** throughout (FastAPI + asyncpg)
- **Connection pooling** (SQLAlchemy)
- **Stateless API** (session_id in request, state in DB)

### Scaling Strategies

**Horizontal Scaling:**
1. Deploy multiple backend instances behind load balancer
2. PostgreSQL read replicas for analytics
3. CDN for frontend static assets

**Performance Optimization:**
1. Vector index optimization (IVFFlat, HNSW)
2. Redis caching for frequently accessed KB chunks
3. Batch embedding generation

**Production Readiness:**
- ✅ Docker containerization
- ✅ Environment-based configuration
- ✅ Structured logging
- ✅ Health check endpoints
- ⚠️ Add monitoring (Prometheus/Grafana)
- ⚠️ Add rate limiting (Redis + Slowapi)

---

## Technology Stack

**Backend:**
- FastAPI 0.104 (async web framework)
- PostgreSQL 16 + pgvector
- SQLAlchemy 2.0 (async ORM)
- Pydantic 2.5 (validation)
- OpenAI GPT-4 Turbo + embeddings
- LangChain (RAG utilities)

**Frontend:**
- React 18
- Vite (build tool)
- Material-UI (components)
- Chart.js (analytics)
- React Markdown

**Infrastructure:**
- Docker + Docker Compose
- Python 3.10
- Node.js 18

---

## Configuration Management

**Environment Variables:**
```bash
# Required
OPENAI_API_KEY          # OpenAI API key
DATABASE_URL_OVERRIDE   # PostgreSQL connection string

# Optional
POSTGRES_SERVER         # Default: localhost
POSTGRES_PORT           # Default: 5432
VECTOR_STORE_TYPE       # postgres | local (default: postgres)
BACKEND_CORS_ORIGINS    # Allowed origins
```

**Configuration File:** `backend/app/core/config.py`
- Uses Pydantic Settings
- Validates on startup
- Environment-based overrides

---

## Design Decisions

### Why PostgreSQL + pgvector?
- **Single database** for relational + vector data
- **ACID compliance** for conversations/tickets
- **Native vector search** (no separate vector DB)
- **Production-ready** (mature, battle-tested)

### Why FastAPI?
- **Async support** (high concurrency)
- **Automatic API docs** (Swagger/OpenAPI)
- **Type safety** (Pydantic integration)
- **Performance** (comparable to Node.js/Go)

### Why Deterministic Tier Classification?
- **Consistency** - same input → same result
- **Auditability** - no AI black box
- **Speed** - pattern matching faster than LLM
- **Cost** - no API calls for classification

### Why RAG over Fine-tuning?
- **Flexibility** - KB updates without retraining
- **Accuracy** - grounded in actual documents
- **Cost-effective** - no fine-tuning costs
- **Transparency** - sources are citeable

---

## Future Enhancements

**Phase 1 (Current):**
- ✅ Core RAG functionality
- ✅ Guardrails & security
- ✅ PostgreSQL persistence
- ✅ Basic analytics

**Phase 2 (Next):**
- [ ] Multi-language support
- [ ] Advanced analytics (ML insights)
- [ ] Integration with ticketing systems (Jira, ServiceNow)
- [ ] Voice input/output

**Phase 3 (Future):**
- [ ] Multi-tenant support
- [ ] Knowledge graph enhancement
- [ ] Federated search across multiple KBs
- [ ] Agent handoff workflow

---

## Monitoring & Observability

**Currently Implemented:**
- Structured logging (app.core.logging)
- Request/response logging
- Error tracking

**Recommended Additions:**
- **APM:** New Relic, Datadog, or OpenTelemetry
- **Metrics:** Prometheus + Grafana
- **Alerting:** PagerDuty for critical issues
- **Log aggregation:** ELK stack or Loki

---

## Compliance & Security

**Data Privacy:**
- Conversation data stored in PostgreSQL
- No data sent to third parties (except OpenAI for LLM)
- Environment-based secrets management

**Security Measures:**
- CORS configuration
- Input validation (Pydantic)
- SQL injection prevention (ORM)
- Rate limiting (recommended addition)

**Audit Trail:**
- All messages logged with timestamps
- Tier classification recorded
- Guardrail activations tracked

---

This architecture is designed for **production readiness**, **scalability**, and **maintainability** while meeting all assessment requirements.
