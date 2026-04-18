"""
FastAPI main application - orchestrates all API routes and middleware.

Startup sequence:
  1. Initialize the PostgreSQL database (create tables, seed test user).
  2. Start the APScheduler background scheduler — runs global job scraping
     every PIPELINE_INTERVAL_HOURS (default 12).
  3. Register all API routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""

    # ── 1. Database ───────────────────────────────────────────────────────────
    logger.info("Starting up FastAPI application…")
    try:
        from backend.app.db.database import init_db
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as exc:
        logger.error(f"✗ Database initialization failed: {exc}", exc_info=True)
        # Continue — might be a transient issue on first deploy

    # ── 2. Background scheduler (global pipeline every 12 h) ─────────────────
    try:
        from backend.app.scheduler import start_scheduler
        start_scheduler()
        logger.info("✓ APScheduler started")
    except Exception as exc:
        logger.error(f"✗ Scheduler failed to start: {exc}", exc_info=True)

    yield  # ── Application is running ────────────────────────────────────────

    # ── 3. Shutdown ───────────────────────────────────────────────────────────
    try:
        from backend.app.scheduler import stop_scheduler
        stop_scheduler()
        logger.info("✓ Scheduler stopped")
    except Exception as exc:
        logger.warning(f"Scheduler shutdown warning: {exc}")

    logger.info("FastAPI application shut down.")


# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Job Recommendation SaaS API",
    description="AI-powered job recommendation platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Default: allow localhost dev ports + deployed Vercel frontend.
# Override via env var ALLOWED_ORIGINS (comma-separated list).
_default_origins = (
    "http://localhost:3000,"
    "http://localhost:3001,"
    "http://localhost:5173,"
    "https://personal-job-recommendation-system.vercel.app"
)
origins = os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    """Health check — used by Railway/Render uptime monitoring."""
    return {"status": "ok", "message": "Backend API is running"}


# ── Routers ────────────────────────────────────────────────────────────────────
try:
    from backend.app.api import jobs, applications, pipeline, stats, auth
    app.include_router(auth.router)
    app.include_router(jobs.router)
    app.include_router(applications.router)
    app.include_router(pipeline.router)
    app.include_router(stats.router)
    logger.info("✓ All API routers loaded successfully")
except Exception as exc:
    logger.error(f"✗ Failed to load API routers: {exc}", exc_info=True)


# ── Global exception handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )

