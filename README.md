# Job_Aggregation--Tracking_Platform

An automated pipeline that aggregates tech jobs and internships from multiple public APIs, filters and classifies them using AI, and delivers curated recommendations to Google Sheets—minimizing manual search effort for job seekers.

---

## Overview

Finding relevant tech internships and entry-level roles across multiple job boards is time-consuming. This system automates the entire workflow: collecting listings from free job APIs, intelligently filtering for software engineering, AI/ML, and related domains, and organizing results in a structured Google Sheet with India and Global job tabs.

---

## Tech Stack

| Component | Technologies |
|-----------|-------------|
| **Language** | Python 3 |
| **HTTP Client** | `httpx`, `requests` |
| **AI Processing** | Groq (Llama 3.3), Gemini, Claude, OpenRouter |
| **Storage** | Google Sheets API (`gspread`) |
| **Authentication** | `google-auth`, `python-dotenv` |
| **Scheduling** | `schedule` |
| **Data Handling** | `pandas` |

---

## Key Features

- **Multi-Source Aggregation** — Fetches from Remotive, Arbeitnow, The Muse, and FindWork APIs
- **AI-Powered Filtering** — Uses LLMs to classify jobs by domain (AI/ML, Frontend, Backend, DevOps, etc.) and prioritize internships
- **Smart Deduplication** — Prevents duplicate entries using job ID tracking
- **Organized Storage** — Auto-creates Google Sheets tabs: 🇮🇳 India Jobs, 🌍 Global Jobs, 📋 All Jobs, 📊 Summary, 🕐 Run History
- **Notifications** — Optional Telegram alerts for new listings
- **Scheduled Execution** — Run on-demand or schedule recurring updates every N hours

---

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Job APIs    │ →  │ Collectors  │ →  │ AI Filter   │ →  │ Google      │
│ (Remotive,  │    │ (Normalize, │    │ (Classify,  │    │ Sheets      │
│  Muse, etc) │    │  Deduplicate│    │  Clean)     │    │ (Organized) │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

1. **Collection** — Fetches jobs from 4 public APIs with internship-first keyword targeting
2. **Processing** — AI backend filters by domain, assigns categories, normalizes locations
3. **Storage** — Uploads to categorized tabs with color-coded rows and summary dashboard
4. **Persistence** — Tracks seen IDs to avoid duplicates across runs

---

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd Personal-job-recommendation-system

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your API keys
```

---

## Configuration

Create a `.env` file with:

```env
# AI Backend (groq/gemini/claude/openrouter)
AI_BACKEND=groq
AI_API_KEY=your_key_here
AI_MODEL=llama-3.3-70b-versatile

# Google Sheets
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEET_NAME=Global Tech Jobs Pipeline
GOOGLE_SHEET_EMAIL=your_email@gmail.com

# Optional: Telegram notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

**Required Setup:**
- Download Google Service Account credentials JSON from GCP Console
- Place as `credentials.json` in project root
- Share your Google Sheet with the service account email

---

## Usage

```bash
# Run once
python main.py

# Run with filters
python main.py --filter remote    # Remote-only roles
python main.py --filter intern    # Internships only

# Scheduled execution (every 6 hours)
python main.py --schedule

# With Telegram notifications
python main.py --schedule --notify
```

---

## 📚 Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Complete setup and deployment guide
- **[IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)** - Project status and feature checklist
- **[backend/README.md](./backend/README.md)** - Backend API documentation
- **[frontend/README.md](./frontend/README.md)** - Frontend setup guide

---

## Future Improvements

- **Email Alerts** — Add email notification support alongside Telegram
- **OAuth Integration** — Google, GitHub, Supabase Auth support
- **Resume Matching** — AI-powered matching between job descriptions and user resumes
- **Kanban Board** — Visual application tracking with drag-and-drop
- **Advanced Analytics** — Trends, recommendations, job market insights
- **Mobile App** — React Native application for iOS/Android
- **More Sources** — Integrate LinkedIn, Indeed, and company career pages via scraping
- **API for Integrations** — Third-party webhook and REST API access

---

## 🎯 Project Status

✅ **Phase 1: Backend API** - Complete  
✅ **Phase 2: Frontend UI** - Complete  
✅ **Phase 3: Integration** - Complete  
✅ **Phase 4: Bug Fixes** - Complete  
✅ **Phase 5: Documentation** - Complete  

**Overall Status**: 🚀 **PRODUCTION READY**

---

**Developed by Priyanshu**
