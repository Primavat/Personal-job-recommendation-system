"""
config.py — centralised configuration loaded from .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── AI Backend ───────────────────────────────────────────────────────────
    AI_BACKEND: str      = os.getenv("AI_BACKEND", "groq")
    AI_API_KEY: str      = os.getenv("AI_API_KEY", "")
    AI_MODEL: str        = os.getenv("AI_MODEL", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    CLAUDE_BATCH_SIZE: int = int(os.getenv("CHUNK_SIZE", "8"))
    CLAUDE_MAX_TOKENS: int = 4000
    CHUNK_SLEEP: float     = float(os.getenv("CHUNK_SLEEP", "15"))  # seconds between chunks

    # ── Google Sheets ────────────────────────────────────────────────────────
    GOOGLE_CREDENTIALS_FILE: str  = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_SHEET_NAME: str        = os.getenv("GOOGLE_SHEET_NAME", "Global Tech Jobs Pipeline")
    GOOGLE_SHEET_EMAIL: str       = os.getenv("GOOGLE_SHEET_EMAIL", "")
    GOOGLE_AUTH_METHOD: str       = os.getenv("GOOGLE_AUTH_METHOD", "service_account")
    GOOGLE_OAUTH_CLIENT_FILE: str = os.getenv("GOOGLE_OAUTH_CLIENT_FILE", "oauth_client.json")

    # ── Job APIs ─────────────────────────────────────────────────────────────
    REMOTIVE_API_URL: str  = "https://remotive.com/api/remote-jobs"
    ARBEITNOW_API_URL: str = "https://www.arbeitnow.com/api/job-board-api"
    FINDWORK_API_KEY: str  = os.getenv("FINDWORK_API_KEY", "")
    FINDWORK_API_URL: str  = "https://findwork.dev/api/jobs/"
    MUSE_API_URL: str      = "https://www.themuse.com/api/public/jobs"

    # ── Telegram (optional) ──────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str   = os.getenv("TELEGRAM_CHAT_ID", "")

    # ── Paths ────────────────────────────────────────────────────────────────
    BASE_DIR: Path      = Path(__file__).parent
    SEEN_IDS_FILE: Path = BASE_DIR / "data" / "seen_ids.txt"
    LOG_FILE: Path      = BASE_DIR / "logs" / "pipeline.log"

    # ── Domain filter ────────────────────────────────────────────────────────
    TARGET_DOMAINS = [
        "Software Engineering", "Software Development",
        "Artificial Intelligence", "Machine Learning", "Deep Learning",
        "Frontend Development", "Web Development",
        "Backend Development", "Full Stack",
        "Quantum Computing", "Data Engineering",
        "DevOps", "Cloud Engineering", "Cybersecurity",
    ]

    ROLE_CATEGORIES = [
        "Software Engineering", "AI / ML", "Frontend / Web",
        "Backend / Full Stack", "Data Engineering", "DevOps / Cloud",
        "Quantum Computing", "Cybersecurity", "Other Tech",
    ]
