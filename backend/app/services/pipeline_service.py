"""
Pipeline service - wrapper around existing collectors and processors.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path
import sys
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.models.models import Job, PipelineRun, PipelineRunStatus, Application, ApplicationStatus
from backend.app.db.schemas import PipelineRunResponse

logger = logging.getLogger(__name__)


class PipelineService:
    """Service to orchestrate job collection, processing, and storage."""

    def __init__(self, db: Session):
        self.db = db

    def run_pipeline(
        self,
        user_id: str,
        job_filter: Optional[str] = None,
    ) -> PipelineRunResponse:
        """
        Run the complete pipeline:
        1. Collect from APIs
        2. Process with Claude/LLM
        3. Store in database
        4. Return statistics

        Args:
            user_id: Current user ID
            job_filter: Optional filter ("remote", "intern", or None)

        Returns:
            PipelineRunResponse with execution stats
        """
        run = PipelineRun(
            user_id=user_id,
            started_at=datetime.now(timezone.utc),
            status=PipelineRunStatus.RUNNING,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        try:
            from config import Config
            from collectors import JobCollector
            from claude_processor import ClaudeProcessor
            from utils import load_seen_ids, save_seen_ids

            cfg = Config()
            seen_ids = load_seen_ids(cfg.SEEN_IDS_FILE)

            # ── Phase 1: Collect ──────────────────────────────────────
            logger.info(f"[User {user_id}] Collecting jobs...")
            collector = JobCollector(cfg)
            raw_jobs = collector.collect_all()
            run.jobs_collected = len(raw_jobs)

            if not raw_jobs:
                logger.warning(f"[User {user_id}] No jobs collected")
                run.ended_at = datetime.now(timezone.utc)
                run.status = PipelineRunStatus.COMPLETED
                self.db.commit()
                return PipelineRunResponse.model_validate(run)

            # ── Phase 2: Deduplicate against history ───────────────────
            new_jobs = [j for j in raw_jobs if j["id"] not in seen_ids]
            logger.info(f"[User {user_id}] {len(new_jobs)} new jobs after dedup")

            if not new_jobs:
                run.jobs_added = 0
                run.ended_at = datetime.now(timezone.utc)
                run.status = PipelineRunStatus.COMPLETED
                self.db.commit()
                return PipelineRunResponse.model_validate(run)

            # ── Phase 3: Claude: filter, classify, clean ──────────────
            logger.info(f"[User {user_id}] Processing with Claude...")
            processor = ClaudeProcessor(cfg)
            processed = processor.process_batch(new_jobs)
            run.jobs_processed = len(processed)

            # ── Phase 4: Optional user-side filter ────────────────────
            if job_filter == "remote":
                processed = [j for j in processed
                           if "remote" in (j.get("location") or "").lower()]
            elif job_filter == "intern":
                processed = [j for j in processed
                           if j.get("job_type", "").lower() == "internship"]

            if not processed:
                run.jobs_added = 0
                run.ended_at = datetime.now(timezone.utc)
                run.status = PipelineRunStatus.COMPLETED
                self.db.commit()
                return PipelineRunResponse.model_validate(run)

            # ── Phase 5: Store in database ────────────────────────────
            logger.info(f"[User {user_id}] Storing jobs in database...")
            added = 0
            for job_data in processed:
                # Check if job already exists
                existing = self.db.query(Job).filter(Job.id == job_data["id"]).first()
                if existing:
                    continue

                job = Job(
                    id=job_data["id"],
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    job_type=job_data["job_type"],
                    category=job_data.get("category", "Other Tech"),
                    description=job_data.get("description", ""),
                    ai_summary=job_data.get("summary", ""),
                    source=job_data["source"],
                    apply_link=job_data["apply_link"],
                    tags=job_data.get("tags", ""),
                    date_posted=job_data["date_posted"],
                )
                self.db.add(job)
                added += 1

            self.db.commit()

            # ── Phase 6: Persist seen IDs ─────────────────────────────
            for j in processed:
                seen_ids.add(j["id"])
            save_seen_ids(cfg.SEEN_IDS_FILE, seen_ids)

            # ── Update run status ─────────────────────────────────────
            run.jobs_added = added
            run.ended_at = datetime.now(timezone.utc)
            run.status = PipelineRunStatus.COMPLETED
            self.db.commit()

            logger.info(f"[User {user_id}] Pipeline complete: {added} jobs added")

            return PipelineRunResponse.model_validate(run)

        except Exception as e:
            logger.error(f"[User {user_id}] Pipeline error: {e}", exc_info=True)
            run.status = PipelineRunStatus.FAILED
            run.error_log = str(e)
            run.ended_at = datetime.now(timezone.utc)
            self.db.commit()
            raise

    def get_pipeline_history(self, user_id: str, limit: int = 10) -> List[PipelineRunResponse]:
        """Get user's pipeline run history."""
        runs = (
            self.db.query(PipelineRun)
            .filter(PipelineRun.user_id == user_id)
            .order_by(PipelineRun.started_at.desc())
            .limit(limit)
            .all()
        )
        return [PipelineRunResponse.model_validate(run) for run in runs]

    def get_latest_run(self, user_id: str) -> Optional[PipelineRunResponse]:
        """Get user's most recent pipeline run."""
        run = (
            self.db.query(PipelineRun)
            .filter(PipelineRun.user_id == user_id)
            .order_by(PipelineRun.started_at.desc())
            .first()
        )
        return PipelineRunResponse.model_validate(run) if run else None
