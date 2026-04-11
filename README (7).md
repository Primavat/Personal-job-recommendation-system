# 🌍 Global Tech Jobs & Internships Pipeline

Automatically fetches tech job listings from public APIs, filters and classifies
them with Claude AI, and uploads structured data to Google Sheets — on a schedule.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Orchestrator)                  │
└───┬──────────────┬────────────────┬───────────────┬─────────┘
    │              │                │               │
    ▼              ▼                ▼               ▼
collectors.py  claude_processor  sheets_manager  notifier.py
(4 APIs)       (filter/classify)  (Google Sheets) (Telegram)
    │              │                │
    ▼              ▼                ▼
Remotive       Anthropic API     gspread
Arbeitnow      claude-sonnet     Google Sheets API
FindWork       ──────────────    ─────────────────
The Muse       • Domain filter   • Auto-create sheet
               • Classify role   • Deduplicate rows
               • Clean data      • Colour by category
               • Summarise       • Run History tab
```

### Data Flow

1. **Collect** — fetch raw jobs from 4 public APIs (keyword + category filtered)
2. **Claude AI** — validate domain, assign category, clean fields, summarise
3. **Dedup** — check `seen_ids.txt` (cross-run) + existing sheet links
4. **Upload** — append new rows with formatting to Google Sheets
5. **Notify** — optional Telegram message with top 5 new roles
6. **Schedule** — runs every N hours via `schedule` library

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API keys

#### Anthropic (Claude)
1. Sign up at https://console.anthropic.com
2. Create an API key → add to `.env` as `ANTHROPIC_API_KEY`

#### Google Sheets (Service Account)
1. Go to https://console.cloud.google.com
2. Create a project → enable **Google Sheets API** + **Google Drive API**
3. Create a **Service Account** → download the JSON key as `credentials.json`
4. Place `credentials.json` in the project folder

#### FindWork (optional, free)
1. Sign up at https://findwork.dev → get API token
2. Add to `.env` as `FINDWORK_API_KEY`

#### Telegram (optional)
1. Message @BotFather → `/newbot` → copy the token
2. Message your bot, then: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   to find your `chat_id`
3. Add both to `.env`

### 3. Configure `.env`

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 4. Run

```bash
# One-time run
python main.py

# Internships only
python main.py --filter intern

# Remote roles only
python main.py --filter remote

# With Telegram notification
python main.py --notify

# Scheduled (every 6 hours, runs immediately then repeats)
python main.py --schedule

# Scheduled every 12 hours
python main.py --schedule --interval 12
```

### 5. Cron setup (Linux/macOS)

```bash
crontab -e
# Add this line — runs every 6 hours:
0 */6 * * * cd /path/to/job_pipeline && python main.py >> logs/cron.log 2>&1
```

### 6. Windows Task Scheduler

```
Action: Start a program
Program: python
Arguments: C:\path\to\job_pipeline\main.py
Start in: C:\path\to\job_pipeline
Trigger: Daily, repeat every 6 hours
```

---

## Google Sheet Structure

### "Jobs" Tab

| Column | Description |
|--------|-------------|
| Job Title | Cleaned, title-cased role name |
| Company | Company name |
| Location | Remote / City, Country / Hybrid |
| Type | Internship / Full-time / Part-time / Contract |
| Category | AI/ML / Frontend-Web / Software Engineering / etc. |
| Tags / Skills | Comma-separated tech skills/tags |
| Date Posted | YYYY-MM-DD |
| Source | Remotive / Arbeitnow / FindWork / The Muse |
| Apply Link | Clickable URL |
| AI Summary | 1-2 sentence Claude summary |
| Row Added | UTC timestamp of when row was added |

Rows are colour-coded by category. Row 1 is frozen. Column widths are pre-set.

### "Run History" Tab

Tracks each automated run: timestamp, new jobs added, total in sheet, sources used.

---

## Folder Structure

```
job_pipeline/
├── main.py               # Orchestrator + CLI
├── config.py             # All settings from .env
├── collectors.py         # API fetchers (Remotive, Arbeitnow, FindWork, Muse)
├── claude_processor.py   # Claude AI filter + classify + clean
├── sheets_manager.py     # Google Sheets write + format
├── notifier.py           # Telegram notifications
├── utils.py              # Logging, seen_ids helpers
├── requirements.txt
├── .env.example
├── credentials.json      # ← your Google service account key (not committed)
├── data/
│   └── seen_ids.txt      # Persisted job IDs to prevent re-upload
└── logs/
    └── pipeline.log      # Rotating log file
```

---

## Idempotency

The system prevents duplicate uploads in two ways:
1. **`seen_ids.txt`** — SHA-1 hash of each job's source ID, persisted between runs
2. **Sheet link check** — before appending, loads existing Apply Links from the sheet

Running the script multiple times is safe.

---

## Adding More Job Sources

Add a new method `_fetch_newsite(self) -> list[dict]` in `collectors.py` returning
dicts with keys: `id, title, company, location, job_type, apply_link, date_posted, description, source, tags`.
Then add it to the `sources` list in `collect_all()`.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `ANTHROPIC_API_KEY` missing | Add to `.env` |
| `credentials.json` not found | Download from Google Cloud Console |
| `SpreadsheetNotFound` | Sheet will be auto-created on first run |
| `PERMISSION_DENIED` on Drive | Enable Drive API in Google Cloud project |
| Claude 429 rate-limit | Reduce `CLAUDE_BATCH_SIZE` in `config.py` |
| No jobs collected | Check network; APIs are free and don't need auth (except FindWork) |
