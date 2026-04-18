"""
APScheduler integration for automated global job scraping.

The scheduler is started in the FastAPI lifespan and runs a global pipeline
every 12 hours (configurable via env: PIPELINE_INTERVAL_HOURS).

Global model:
  Jobs are scraped once and stored in the shared `jobs` table.
  All users see the same fresh job pool — no per-user scraping.
"""

import logging
import os
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.app.db.database import SessionLocal
from backend.app.models.models import PipelineRun, PipelineRunStatus

logger = logging.getLogger(__name__)

# ── Singleton scheduler instance ──────────────────────────────────────────────
scheduler = BackgroundScheduler(timezone="UTC")

# Interval in hours (default 12, override via env)
_INTERVAL_HOURS = int(os.getenv("PIPELINE_INTERVAL_HOURS", "12"))

# A sentinel user_id so global runs are identifiable in the DB
_SYSTEM_USER_ID = "system"


def _run_global_pipeline() -> None:
    """
    Scheduled task: run the full pipeline globally.
    Opens its own DB session (scheduler runs outside request context).
    """
    logger.info(f"[Scheduler] Global pipeline triggered at {datetime.now(timezone.utc).isoformat()}")

    db = SessionLocal()
    try:
        # Create a run record attributed to the system user
        run = PipelineRun(
            user_id=_SYSTEM_USER_ID,
            started_at=datetime.now(timezone.utc),
            status=PipelineRunStatus.RUNNING,
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        run_id = run.id
    finally:
        db.close()

    # Execute the heavy work in its own session (execute_pipeline manages its own session)
    from backend.app.services.pipeline_service import PipelineService
    PipelineService.execute_pipeline(run_id=run_id, job_filter=None)

    logger.info(f"[Scheduler] Global pipeline run #{run_id} finished")


def start_scheduler() -> None:
    """Start the background scheduler (called during app startup)."""
    if scheduler.running:
        logger.warning("[Scheduler] Already running — skipping start")
        return

    scheduler.add_job(
        func=_run_global_pipeline,
        trigger=IntervalTrigger(hours=_INTERVAL_HOURS),
        id="global_pipeline",
        name=f"Global job scrape every {_INTERVAL_HOURS}h",
        replace_existing=True,
        # Run once immediately on startup so the DB is populated right away
        next_run_time=None,   # set to datetime.now(timezone.utc) to run on startup
    )

    scheduler.start()
    logger.info(
        f"[Scheduler] Started — global pipeline will run every {_INTERVAL_HOURS} hours"
    )


def stop_scheduler() -> None:
    """Gracefully stop the scheduler (called during app shutdown)."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped")
