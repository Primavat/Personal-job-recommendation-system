# 🚀 Job Recommendation SaaS Platform

AI-powered job recommendation platform that aggregates tech jobs from multiple sources, filters them intelligently with AI, and provides a modern SaaS interface for job seekers.

**Status**: Phase 1 - Backend & Frontend scaffolding complete ✅

---

## 📋 Overview

This is a complete SaaS transformation of the original job recommendation system. It now features:

- ✅ **Backend API** (FastAPI + PostgreSQL/Supabase)
- ✅ **Frontend UI** (Next.js + React + Tailwind CSS)
- ✅ **Multi-user support** with Supabase Auth
- ✅ **Job search & filtering** with AI categorization
- ✅ **Application tracking** (Kanban-style status tracking)
- ✅ **Analytics dashboard** with insights
- ✅ **Pipeline orchestration** (collect → process → store)
- ✅ **Responsive design** (mobile-first)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                                                 │
│         Frontend (Next.js + React)              │
│  - Dashboard, Job Browse, Applications          │
│  - Filters, Search, Analytics                   │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │ API via Axios
                 ▼
┌─────────────────────────────────────────────────┐
│                                                 │
│         Backend (FastAPI)                       │
│  - REST API endpoints                           │
│  - Pipeline orchestration                       │
│  - Job aggregation logic                        │
│  - Auth & user isolation                        │
│                                                 │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│                                                 │
│    PostgreSQL (via Supabase)                    │
│  - Users, Jobs, Applications                    │
│  - Pipeline runs, Preferences                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py                  # FastAPI app
│   │   ├── auth.py                  # JWT authentication
│   │   ├── api/                     # Route handlers
│   │   │   ├── jobs.py              # Job endpoints
│   │   │   ├── applications.py      # Application endpoints
│   │   │   ├── pipeline.py          # Pipeline endpoints
│   │   │   └── stats.py             # Analytics endpoints
│   │   ├── models/
│   │   │   └── models.py            # SQLAlchemy ORM
│   │   ├── db/
│   │   │   ├── database.py          # DB connection
│   │   │   └── schemas.py           # Pydantic schemas
│   │   └── services/
│   │       ├── job_service.py       # Job logic
│   │       └── pipeline_service.py  # Pipeline logic
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── frontend/                         # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home
│   │   ├── dashboard/               # Dashboard page
│   │   ├── jobs/                    # Job browse page
│   │   ├── applications/            # Application tracker
│   │   ├── analytics/               # Analytics
│   │   ├── settings/                # Settings
│   │   └── login/                   # Auth
│   ├── components/
│   │   ├── Navbar.tsx
│   │   ├── JobCard.tsx
│   │   ├── JobList.tsx
│   │   ├── JobModal.tsx
│   │   └── FilterPanel.tsx
│   ├── lib/
│   │   ├── api.ts                   # API client
│   │   ├── store.ts                 # State management
│   │   └── utils.ts                 # Utilities
│   ├── package.json
│   ├── tailwind.config.ts
│   └── README.md
│
├── docker-compose.yml               # Local dev setup
├── Dockerfile.backend               # Backend image
├── .env.example                     # Config template
└── README.md (this file)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)
- Supabase account (or PostgreSQL)

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repo-url>
cd Personal-job-recommendation-system

# Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit files with your API keys and config
# - backend/.env: AI backend (Groq/Gemini), Supabase
# - frontend/.env.local: API URL, Supabase keys

# Start everything
docker-compose up -d

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your configuration

python -c "from app.db.database import init_db; init_db()"
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration

npm run dev
```

---

## 📖 API Endpoints

### Jobs
- `GET /api/jobs` - List jobs with filters
- `GET /api/jobs/{id}` - Job details
- `GET /api/jobs/filters/categories` - Available categories
- `GET /api/jobs/filters/sources` - Available sources
- `GET /api/jobs/filters/locations` - Available locations

### Applications
- `GET /api/applications` - User's applications
- `POST /api/applications/{job_id}/save` - Save job
- `DELETE /api/applications/{job_id}/save` - Unsave job
- `PATCH /api/applications/{job_id}` - Update status
- `GET /api/applications/{job_id}` - Application details

### Pipeline
- `POST /api/pipeline/run` - Start job collection
- `GET /api/pipeline/history` - Run history
- `GET /api/pipeline/status` - Latest status

### Analytics
- `GET /api/stats/overview` - Dashboard stats
- `GET /api/stats/by-category` - Jobs by category
- `GET /api/stats/by-source` - Jobs by source
- `GET /api/stats` - Complete analytics

---

## 🔐 Authentication

Uses **Supabase Auth** for secure user management:

1. Sign up/login via Supabase (emails, OAuth)
2. Receive JWT token
3. Token stored in localStorage
4. Included in `Authorization: Bearer <token>` header
5. Backend validates and returns user-specific data

---

## 🎯 Features

### Current (Phase 1)
- ✅ Frontend scaffolding with all pages
- ✅ Backend API with all endpoints
- ✅ Database models and ORM
- ✅ Job search and filtering
- ✅ Application tracking
- ✅ Analytics dashboard
- ✅ Pipeline control
- ✅ Responsive design

### Next (Phase 2)
- 🔄 Supabase Auth integration
- 🔄 Real-time job updates
- 🔄 Advanced filtering with preferences
- 🔄 Email notifications
- 🔄 Resume upload & matching
- 🔄 More AI features

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS, Zustand |
| **Backend** | FastAPI, SQLAlchemy, Pydantic, Python 3.11 |
| **Database** | PostgreSQL (via Supabase) |
| **Auth** | Supabase Auth (JWT) |
| **Hosting** | Vercel (frontend), Railway/Render (backend) |
| **AI** | Groq/Gemini/Claude (configurable) |

---

## 📚 Documentation

- [Backend README](./backend/README.md) - API setup and usage
- [Frontend README](./frontend/README.md) - UI development guide

---

## 🔗 Environment Variables

### Backend (`.env`)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/job_recommendations
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
JWT_SECRET=your-secret
AI_BACKEND=groq
AI_API_KEY=your-api-key
```

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

---

## 🚀 Deployment

### Frontend (Vercel)
```bash
# Connect GitHub repo to Vercel
# Environment variables auto-synced
vercel deploy
```

### Backend (Railway/Render)
```bash
# Connect GitHub repo
# Set environment variables
# Auto-deploys on push
```

### Database (Supabase)
- Managed PostgreSQL
- Built-in backups
- Real-time capabilities

---

## 📊 Data Models

### Users
- id (UUID)
- email
- created_at

### Jobs
- id (SHA1 hash)
- title, company, location
- job_type, category
- source (Remotive, Arbeitnow, Muse, FindWork)
- ai_summary, apply_link
- created_at

### Applications
- id (int)
- user_id, job_id
- status (saved, applied, rejected, interviewed, offered)
- notes, applied_date
- created_at

### Pipeline Runs
- id (int)
- user_id
- started_at, ended_at
- status (running, completed, failed)
- jobs_collected, jobs_processed, jobs_added
- error_log

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/my-feature`
5. Open a pull request

---

## 📝 Development Workflow

```bash
# Setup
docker-compose up -d

# Backend development
cd backend
uvicorn app.main:app --reload

# Frontend development (new terminal)
cd frontend
npm run dev

# Make changes, test, commit
git add .
git commit -m "Your message"
git push
```

---

## 🐛 Troubleshooting

### Backend won't start
- Check `.env` file is copied and configured
- Ensure PostgreSQL is running
- Check port 8000 is available

### Frontend can't connect to API
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is running on that URL
- Check CORS settings in backend

### Jobs not showing up
- Confirm pipeline has been run
- Check database has jobs (query directly)
- Verify API endpoint returns data

---

## 📞 Support

Found a bug? Have a feature idea?
- Open an issue on GitHub
- Check existing issues first
- Include reproducible steps

---

## 📄 License

[Add your license here]

---

## 🙏 Acknowledgments

Built with:
- [Next.js](https://nextjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Supabase](https://supabase.com/)

Original system by: Primavat
SaaS transformation: 2026

---

**Ready to transform your job search? Deploy now!** 🚀
