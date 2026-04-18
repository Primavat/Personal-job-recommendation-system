"""
API endpoints for pipeline operations (job collection and processing).

The /run endpoint is fire-and-forget:
  1. Creates a PipelineRun DB record immediately.
  2. Returns 202 ACCEPTED with the run record (status=running).
  3. Dispatches the heavy work (collect → AI → store) as a FastAPI BackgroundTask
     so the HTTP connection is never held open for minutes.

The frontend polls /status every few seconds to track progress.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.db.database import get_db
from backend.app.auth import get_current_user
from backend.app.db.schemas import PipelineRunResponse
from backend.app.services.pipeline_service import PipelineService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_pipeline(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    job_filter: Optional[str] = Query(None, description="Filter: 'remote' or 'intern'"),
):
    """
    Trigger the job collection and processing pipeline (non-blocking).

    Returns 202 ACCEPTED immediately with a PipelineRun showing status=running.
    The actual pipeline runs in the background — poll /api/pipeline/status to
    track when it transitions to completed or failed.
    """
    try:
        service = PipelineService(db)
        # Step 1 — create the DB record and return it right away
        run_response = service.create_pipeline_run(user_id=user_id)

        # Step 2 — dispatch the heavy work to run after this response is sent
        background_tasks.add_task(
            PipelineService.execute_pipeline,
            run_id=run_response.id,
            job_filter=job_filter,
        )

        logger.info(
            f"[API] Pipeline run #{run_response.id} queued for user {user_id}"
        )
        return run_response

    except Exception as exc:
        logger.error(f"[API] Failed to trigger pipeline: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger pipeline: {str(exc)}",
        )


@router.get("/history", response_model=dict)
def get_pipeline_history(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Get user's pipeline execution history (most recent first).
    """
    service = PipelineService(db)
    runs = service.get_pipeline_history(user_id=user_id, limit=limit)
    return {"items": runs, "total": len(runs)}


@router.get("/status", response_model=Optional[PipelineRunResponse])
def get_pipeline_status(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Get the latest pipeline run status for the authenticated user.
    Poll this endpoint to track background pipeline progress.
    """
    service = PipelineService(db)
    return service.get_latest_run(user_id=user_id)
