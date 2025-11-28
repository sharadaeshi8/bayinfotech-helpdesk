# Local Development with PostgreSQL + pgvector

This guide explains how to run the backend locally using PostgreSQL with pgvector via Docker.

## Quick Start

### 1. Install Docker

Make sure you have Docker and Docker Compose installed:
```bash
docker --version
docker-compose --version
```

### 2. Start PostgreSQL Database

From the project root directory:

```bash
# Start PostgreSQL with pgvector
docker-compose up -d postgres

# Check if it's running
docker ps
```

You should see a container named `helpdesk-postgres` running.

### 3. Update Environment Variables

Update `backend/.env` (create from `.env.example` if needed):

```bash
# Copy example if needed
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```bash
VECTOR_STORE_TYPE=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=helpdesk

# Add your OpenAI API key
OPENAI_API_KEY=sk-your-openai-api-key
```

### 4. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Run Backend Manually

```bash
# From backend directory
uvicorn app.main:app --reload
```

The backend will:
- Start on http://localhost:8000
- Automatically create database tables
- Enable pgvector extension

### 6. Ingest Knowledge Base Documents

In a new terminal:

```bash
cd backend
python -m app.scripts.ingest
```

Expected output:
```
Initializing PostgreSQL database...
pgvector extension enabled
Database tables created successfully
Database initialized.
Ingesting KB documents from data/kb...
Processing article1.md...
...
Ingestion complete and saved to PostgreSQL.
```

---

## Alternative: Run Everything with Docker Compose

To run both PostgreSQL AND backend in Docker:

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop everything
docker-compose down

# Stop and remove data (fresh start)
docker-compose down -v
```

---

## Verify Setup

### Check Database

Connect to PostgreSQL:
```bash
docker exec -it helpdesk-postgres psql -U postgres -d helpdesk
```

Run these commands:
```sql
-- Check if pgvector is installed
SELECT * FROM pg_extension WHERE extname='vector';

-- Check if documents table exists
\dt

-- Count documents
SELECT COUNT(*) FROM documents;

-- View a sample document
SELECT id, LEFT(content, 100), metadata FROM documents LIMIT 1;

-- Exit
\q
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000

# Test chat (requires frontend or use curl with JSON)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test123","message":"How do I reset my password?","role":"user"}'
```

---

## Switching Between Local and PostgreSQL

### Use Local FAISS Store

Update `backend/.env`:
```bash
VECTOR_STORE_TYPE=local
```

Restart the backend. It will use the `vector_store_data/` directory.

### Use PostgreSQL Store

Update `backend/.env`:
```bash
VECTOR_STORE_TYPE=postgres
```

Restart the backend and re-run ingestion if needed.

---

## Troubleshooting

### Port 5432 Already in Use

If you have PostgreSQL installed locally:

**Option 1**: Stop local PostgreSQL
```bash
sudo service postgresql stop
```

**Option 2**: Change Docker port
Edit `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Changed from 5432:5432
```

Then update `.env`:
```bash
POSTGRES_PORT=5433
```

### Database Connection Refused

```bash
# Check if container is running
docker ps

# Check container logs
docker logs helpdesk-postgres

# Restart container
docker-compose restart postgres
```

### Permission Denied on Docker Volume

```bash
# Remove volumes and recreate
docker-compose down -v
docker-compose up -d postgres
```

### Import Errors

If you get Python import errors:

```bash
# Make sure you're in a virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Useful Commands

```bash
# View all containers
docker ps -a

# View PostgreSQL logs
docker logs -f helpdesk-postgres

# Stop PostgreSQL
docker-compose stop postgres

# Start PostgreSQL
docker-compose start postgres

# Remove PostgreSQL container and data
docker-compose down -v

# Connect to PostgreSQL shell
docker exec -it helpdesk-postgres psql -U postgres -d helpdesk

# Backup database
docker exec helpdesk-postgres pg_dump -U postgres helpdesk > backup.sql

# Restore database
docker exec -i helpdesk-postgres psql -U postgres helpdesk < backup.sql
```

---

## Development Workflow

1. Start PostgreSQL: `docker-compose up -d postgres`
2. Start backend: `cd backend && uvicorn app.main:app --reload`
3. Start frontend: `cd frontend && npm run dev`
4. Make code changes (backend auto-reloads)
5. Test changes in frontend
6. Stop services when done: `docker-compose down`

---

## Next Steps

- See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
- Check `backend/README.md` for backend-specific documentation
- Check `frontend/README.md` for frontend-specific documentation
