# Deployment Guide: Render + Supabase

This guide will walk you through deploying the AI Help Desk backend to Render.com with Supabase as the PostgreSQL database.

## Prerequisites

- GitHub account
- Supabase account (free tier)
- Render account (free tier)
- OpenAI API key

---

## Part 1: Set Up Supabase Database

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **"New Project"**
3. Fill in the details:
   - **Name**: `helpdesk-db` (or any name you prefer)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose the closest region to your users
   - **Pricing Plan**: Free
4. Click **"Create new project"**
5. Wait 2-3 minutes for the database to be provisioned

### Step 2: Enable pgvector Extension

1. In your Supabase project, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Run this SQL command:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Click **"Run"** or press `Ctrl+Enter`
5. You should see: "Success. No rows returned"

### Step 3: Get Connection Details

1. Go to **Project Settings** → **Database** (left sidebar)
2. Scroll down to **Connection string** section
3. Copy the **URI** format connection string (it looks like):
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres
   ```
4. **Important**: Replace `[YOUR-PASSWORD]` with your actual database password
5. Save this connection string - you'll need it later

---

## Part 2: Prepare Code for Deployment

### Step 1: Update .env.example

Your `.env.example` should already have the PostgreSQL settings. Users will configure their own `.env` file.

### Step 2: Push Code to GitHub

```bash
# From your project root
cd /home/dev/Desktop/assesment/bayinfotech-helpdesk

# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Add PostgreSQL with pgvector support"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/bayinfotech-helpdesk.git
git branch -M main
git push -u origin main
```

---

## Part 3: Deploy Backend to Render

### Step 1: Create Web Service

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository:
   - Click **"Connect account"** if needed
   - Select the `bayinfotech-helpdesk` repository
4. Configure the service:
   - **Name**: `helpdesk-backend` (or any name)
   - **Region**: Same as your Supabase region (if possible)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### Step 2: Set Environment Variables

In the **Environment** section, add these environment variables:

```bash
# Database Configuration (from Supabase)
POSTGRES_SERVER=aws-0-us-west-1.pooler.supabase.com
POSTGRES_PORT=5432
POSTGRES_USER=postgres.xxxxx
POSTGRES_PASSWORD=your-supabase-password
POSTGRES_DB=postgres
VECTOR_STORE_TYPE=postgres

# API Configuration
PROJECT_NAME=AI Help Desk
API_V1_STR=/api/v1

# CORS - Update after deploying frontend
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
```

**Important Notes**:
- Extract `POSTGRES_SERVER` and `POSTGRES_USER` from your Supabase connection string
- For the connection string `postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:5432/postgres`:
  - `POSTGRES_SERVER` = `aws-0-us-west-1.pooler.supabase.com`
  - `POSTGRES_USER` = `postgres.xxxxx`
  - `POSTGRES_PASSWORD` = your database password
  - `POSTGRES_DB` = `postgres`

### Step 3: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your backend
   - Assign you a URL like: `https://helpdesk-backend-xxxx.onrender.com`
3. Wait for the build to complete (5-10 minutes for first deploy)

### Step 4: Verify Deployment

1. Once deployed, click on your service URL
2. You should see: `{"message": "Welcome to AI Help Desk API"}`
3. Test the health endpoint: `https://your-backend-url.onrender.com/health`
4. Should return: `{"status": "healthy"}`

---

## Part 4: Ingest Knowledge Base Data

### Option A: Run Locally (Recommended)

1. On your local machine, update `backend/.env`:
   ```bash
   VECTOR_STORE_TYPE=postgres
   POSTGRES_SERVER=aws-0-us-west-1.pooler.supabase.com
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres.xxxxx
   POSTGRES_PASSWORD=your-supabase-password
   POSTGRES_DB=postgres
   OPENAI_API_KEY=sk-your-openai-api-key
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the ingestion script:
   ```bash
   python -m app.scripts.ingest
   ```

4. You should see output like:
   ```
   Initializing PostgreSQL database...
   Database initialized.
   Ingesting KB documents from data/kb...
   Processing article1.md...
   ...
   Ingestion complete and saved to PostgreSQL.
   ```

### Option B: Using Render Shell

1. In Render dashboard, go to your backend service
2. Click **"Shell"** tab in the top menu
3. Wait for the shell to connect
4. Run:
   ```bash
   python -m app.scripts.ingest
   ```

---

## Part 5: Deploy Frontend to Vercel/Netlify (Optional)

### Update Frontend API URL

1. In `frontend/src/api/` files, update the base URL to your Render backend URL
2. Or use environment variables:
   ```javascript
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
   ```

### Deploy to Vercel

```bash
cd frontend
npx vercel
```

### Update CORS Settings

After deploying frontend, update the `BACKEND_CORS_ORIGINS` environment variable in Render:
```bash
BACKEND_CORS_ORIGINS=["https://your-frontend-url.vercel.app"]
```

---

## Part 6: Monitoring and Maintenance

### Monitor Logs

- **Render**: Go to your service → **Logs** tab
- **Supabase**: Go to **Database** → **Logs**

### Database Management

- View data in Supabase: **Table Editor** → `documents` table
- Run SQL queries: **SQL Editor**

### Troubleshooting

**Backend not starting:**
- Check Render logs for errors
- Verify all environment variables are set correctly
- Ensure database connection string is correct

**Database connection errors:**
- Check Supabase is active and not paused
- Verify connection string is correct
- Check firewall/network settings

**Ingestion failing:**
- Verify OPENAI_API_KEY is valid
- Check you have credits in OpenAI account
- Ensure KB documents exist in `data/kb/` directory

---

## Cost Summary

| Service | Free Tier Limits |
|---------|------------------|
| **Supabase** | 500 MB database, 2 GB bandwidth |
| **Render** | 750 hours/month (spins down after 15 min inactivity) |
| **OpenAI** | Pay-as-you-go (embeddings ~$0.0001/1K tokens) |

**Total Monthly Cost**: $0 (within free tier limits) + OpenAI usage (~$1-5 for typical helpdesk)

---

## Next Steps

1. ✅ Set up Supabase database with pgvector
2. ✅ Deploy backend to Render
3. ✅ Configure environment variables
4. ✅ Ingest knowledge base documents
5. ✅ Test the API endpoints
6. 🔄 Deploy frontend (optional)
7. 🔄 Update CORS settings
8. 🔄 Monitor and scale as needed

**Your backend is now live!** 🚀

For questions or issues, check the logs in Render and Supabase dashboards.
