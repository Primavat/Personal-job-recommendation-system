"""
Pipeline service - background-safe wrapper around collectors and processors.

Architecture:
  - create_pipeline_run()  → Creates a PipelineRun DB record, returns it immediately.
  - execute_pipeline()     → Long-running task. Opens its own DB session so it can
                             safely run in a background thread/task after the HTTP
                             response has already been sent.
  - Global scraping model  → Jobs are collected once and stored globally; all users
                             see the same shared job pool.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List
from pathlib import Path
import sys

from sqlalchemy.orm import Session

from backend.app.models.models import Job, PipelineRun, PipelineRunStatus
from backend.app.db.schemas import PipelineRunResponse
from backend.app.db.database import SessionLocal

logger = logging.getLogger(__name__)

# Add project root to import root-level collectors/config
_project_root = Path(__file__).parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


class PipelineService:
    """Service to orchestrate job collection, processing, and storage."""

    def __init__(self, db: Session):
        self.db = db

    # ──────────────────────────────────────────────────────────────────────────
    # Public: create a run record and return it immediately (non-blocking).
    # The actual work is done in execute_pipeline(), which should be dispatched
    # via FastAPI BackgroundTasks or APScheduler.
    # ──────────────────────────────────────────────────────────────────────────

    def create_pipeline_run(self, user_id: str) -> PipelineRunResponse:
        """
        Create a new PipelineRun record with status=RUNNING and return it.
        Call this before spawning the background task so the API can reply
        immediately with the run ID.
        """
        run = PipelineRun(
            user_id=user_id,
            started_at=datetime.now(timezone.utc),
            status=PipelineRunStatus.RUNNING,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        logger.info(f"[Pipeline] Created run #{run.id} for user {user_id}")
        return PipelineRunResponse.model_validate(run)

    # ──────────────────────────────────────────────────────────────────────────
    # Background worker — opens its own session (request session is closed).
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def execute_pipeline(run_id: int, job_filter: Optional[str] = None) -> None:
        """
        Long-running pipeline execution. Must be called in a background
        context (BackgroundTasks / APScheduler).  Opens its own DB session.

        Global scraping: jobs are stored in the shared `jobs` table so every
        user on the platform benefits from the same crawl.

        Args:
            run_id:     ID of the PipelineRun record created by create_pipeline_run().
            job_filter: Optional post-filter — "remote" | "intern" | None.
        """
        db: Session = SessionLocal()
        try:
            run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()
            if not run:
                logger.error(f"[Pipeline] Run #{run_id} not found in DB")
                return

            # ── Phase 1: Import root-level modules ────────────────────────────
            try:
                from config import Config
                from collectors import JobCollector
                from claude_processor import ClaudeProcessor
                from utils import load_seen_ids, save_seen_ids
            except ImportError as exc:
                logger.error(f"[Pipeline] Import error: {exc}")
                run.status = PipelineRunStatus.FAILED
                run.error_log = f"Import error: {exc}"
                run.ended_at = datetime.now(timezone.utc)
                db.commit()
                return

            cfg = Config()
            seen_ids = load_seen_ids(cfg.SEEN_IDS_FILE)

            # ── Phase 2: Collect ──────────────────────────────────────────────
            logger.info(f"[Pipeline #{run_id}] Collecting jobs from APIs…")
            collector = JobCollector(cfg)
            raw_jobs = collector.collect_all()
            run.jobs_collected = len(raw_jobs)
            db.commit()

            if not raw_jobs:
                logger.warning(f"[Pipeline #{run_id}] No jobs collected")
                _finish_run(db, run, jobs_added=0)
                return

            # ── Phase 3: Deduplicate against seen IDs ─────────────────────────
            new_jobs = [j for j in raw_jobs if j["id"] not in seen_ids]
            logger.info(f"[Pipeline #{run_id}] {len(new_jobs)} new (of {len(raw_jobs)} raw)")

            if not new_jobs:
                _finish_run(db, run, jobs_added=0)
                return

            # ── Phase 4: AI filter + classify ─────────────────────────────────
            logger.info(f"[Pipeline #{run_id}] Running AI processing…")
            processor = ClaudeProcessor(cfg)
            processed = processor.process_batch(new_jobs)
            run.jobs_processed = len(processed)
            db.commit()

            # ── Phase 5: Optional user-side filter ────────────────────────────
            if job_filter == "remote":
                processed = [j for j in processed
                             if "remote" in (j.get("location") or "").lower()]
            elif job_filter == "intern":
                processed = [j for j in processed
                             if j.get("job_type", "").lower() == "internship"]

            if not processed:
                _finish_run(db, run, jobs_added=0)
                return

            # ── Phase 6: Store globally (shared job pool) ──────────────────────
            logger.info(f"[Pipeline #{run_id}] Storing {len(processed)} jobs…")
            added = 0
            for job_data in processed:
                existing = db.query(Job).filter(Job.id == job_data["id"]).first()
                if existing:
                    continue
                job = Job(
                    id=job_data["id"],
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data.get("location", ""),
                    job_type=job_data.get("job_type", ""),
                    category=job_data.get("category", "Other Tech"),
                    description=job_data.get("description", ""),
                    ai_summary=job_data.get("summary", ""),
                    source=job_data["source"],
                    apply_link=job_data["apply_link"],
                    tags=job_data.get("tags", ""),
                    date_posted=job_data["date_posted"],
                )
                db.add(job)
                added += 1

            db.commit()

            # ── Phase 7: Persist seen IDs ─────────────────────────────────────
            for j in processed:
                seen_ids.add(j["id"])
            save_seen_ids(cfg.SEEN_IDS_FILE, seen_ids)

            _finish_run(db, run, jobs_added=added)
            logger.info(f"[Pipeline #{run_id}] Complete — {added} jobs added")

        except Exception as exc:
            logger.error(f"[Pipeline #{run_id}] Error: {exc}", exc_info=True)
            try:
                if run:
                    run.status = PipelineRunStatus.FAILED
                    run.error_log = str(exc)
                    run.ended_at = datetime.now(timezone.utc)
                    db.commit()
            except Exception:
                pass
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────────
    # Query helpers
    # ──────────────────────────────────────────────────────────────────────────

    def get_pipeline_history(self, user_id: str, limit: int = 10) -> List[PipelineRunResponse]:
        """Return the user's pipeline run history (most recent first)."""
        runs = (
            self.db.query(PipelineRun)
            .filter(PipelineRun.user_id == user_id)
            .order_by(PipelineRun.started_at.desc())
            .limit(limit)
            .all()
        )
        return [PipelineRunResponse.model_validate(r) for r in runs]

    def get_latest_run(self, user_id: str) -> Optional[PipelineRunResponse]:
        """Return the user's most recent pipeline run, or None."""
        run = (
            self.db.query(PipelineRun)
            .filter(PipelineRun.user_id == user_id)
            .order_by(PipelineRun.started_at.desc())
            .first()
        )
        return PipelineRunResponse.model_validate(run) if run else None


# ──────────────────────────────────────────────────────────────────────────────
# Private helper
# ──────────────────────────────────────────────────────────────────────────────

def _finish_run(db: Session, run: PipelineRun, jobs_added: int) -> None:
    """Mark a run as COMPLETED and record how many jobs were added."""
    run.jobs_added = jobs_added
    run.ended_at = datetime.now(timezone.utc)
    run.status = PipelineRunStatus.COMPLETED
    db.commit()
