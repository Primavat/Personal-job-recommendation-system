"""
API endpoints for pipeline operations (job collection and processing).
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.database import get_db
from backend.app.auth import get_current_user
from backend.app.db.schemas import PipelineRunResponse
from backend.app.services.pipeline_service import PipelineService

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_pipeline(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    job_filter: Optional[str] = Query(None, description="Filter: 'remote' or 'intern'"),
):
    """
    Trigger the job collection and processing pipeline.

    This endpoint runs the complete pipeline:
    1. Collect jobs from all APIs
    2. Process with Claude/LLM AI
    3. Filter and deduplicate
    4. Store in database

    Returns:
        PipelineRunResponse: Details of the job collection run
    """
    try:
        service = PipelineService(db)
        run = service.run_pipeline(user_id=user_id, job_filter=job_filter)
        return run
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failed: {str(e)}",
        )


@router.get("/history", response_model=dict)
def get_pipeline_history(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Get user's pipeline execution history.

    Returns:
        List of PipelineRunResponse: Past pipeline runs with stats
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
    Get the latest pipeline run status.

    Returns:
        PipelineRunResponse: Status and stats of the most recent run, or null if no runs
    """
    service = PipelineService(db)
    return service.get_latest_run(user_id=user_id)
