# Backend API - Job Recommendation SaaS

FastAPI REST API for the job recommendation platform. Provides endpoints for job search, application tracking, pipeline orchestration, and analytics.

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and start containers
docker-compose up -d

# API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Initialize database (requires PostgreSQL running)
python -c "from backend.app.db.database import init_db; init_db()"

# Run server
uvicorn backend.app.main:app --reload
```

## 🔧 Configuration

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/job_recommendations

# Supabase (for auth)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
JWT_SECRET=your-secret-key

# AI Backend
AI_BACKEND=groq
AI_API_KEY=your-groq-api-key
AI_MODEL=llama-3.3-70b-versatile

# Optional: Job APIs
FINDWORK_API_KEY=optional_key
```

## 📚 API Endpoints

### Jobs
- `GET /api/jobs` - List jobs with filters
- `GET /api/jobs/{id}` - Get job details
- `GET /api/jobs/filters/categories` - Get available categories
- `GET /api/jobs/filters/sources` - Get available sources
- `GET /api/jobs/filters/locations` - Get available locations

### Applications (Saved/Tracked Jobs)
- `GET /api/applications` - List user's applications
- `POST /api/applications/{job_id}/save` - Save job
- `DELETE /api/applications/{job_id}/save` - Unsave job
- `PATCH /api/applications/{job_id}` - Update application status
- `GET /api/applications/{job_id}` - Get application details

### Pipeline (Job Collection)
- `POST /api/pipeline/run` - Trigger job collection
- `GET /api/pipeline/history` - Get pipeline run history
- `GET /api/pipeline/status` - Get latest pipeline status

### Analytics
- `GET /api/stats/overview` - Dashboard overview stats
- `GET /api/stats/by-category` - Jobs by category
- `GET /api/stats/by-source` - Jobs by source
- `GET /api/stats` - Complete analytics

### Health
- `GET /health` - Health check

## 📖 API Documentation

Once running, view interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗄️ Database Schema

### Tables
- **users** - User accounts (from Supabase Auth)
- **jobs** - Aggregated job listings
- **applications** - User's saved/applied jobs
- **pipeline_runs** - Job collection execution history
- **user_preferences** - User settings and pipeline configuration

## 🔐 Authentication

Uses JWT tokens from Supabase Auth. Include token in request header:

```
Authorization: Bearer <jwt_token>
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app setup
│   ├── auth.py              # Auth middleware
│   ├── api/
│   │   ├── jobs.py          # Job endpoints
│   │   ├── applications.py  # Application endpoints
│   │   ├── pipeline.py      # Pipeline endpoints
│   │   └── stats.py         # Analytics endpoints
│   ├── models/
│   │   └── models.py        # SQLAlchemy ORM models
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   └── schemas.py       # Pydantic schemas
│   └── services/
│       ├── job_service.py   # Job business logic
│       └── pipeline_service.py # Pipeline orchestration
├── requirements.txt
├── .env.example
└── Dockerfile
```

## 🚀 Deployment

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Railway/Render
- Connect GitHub repository
- Set environment variables
- Deploy

## 🛠️ Development

### Run tests
```bash
pytest
```

### Format code
```bash
black backend/
```

### Type checking
```bash
mypy backend/
```

## 📝 Notes

- The pipeline service reuses existing collectors and processors from the parent project
- All user data is isolated by user_id (multi-tenant)
- Jobs are shared across users (global job pool)
- Pipeline runs are tracked per user
