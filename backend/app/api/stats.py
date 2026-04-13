"""
API endpoints for analytics and statistics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from backend.app.db.database import get_db
from backend.app.auth import get_current_user
from backend.app.db.schemas import (
    StatsOverviewResponse,
    CategoryStatsResponse,
    SourceStatsResponse,
    AnalyticsResponse,
    PipelineRunResponse,
)
from backend.app.models.models import Job, Application, ApplicationStatus, PipelineRun
from backend.app.services.pipeline_service import PipelineService

router = APIRouter(prefix="/api/stats", tags=["analytics"])


@router.get("/overview", response_model=StatsOverviewResponse)
def get_overview(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get overview statistics for the dashboard."""
    # Total jobs in system
    total_jobs = db.query(func.count(Job.id)).scalar() or 0

    # User's applications
    total_applications = (
        db.query(func.count(Application.id))
        .filter(Application.user_id == user_id)
        .scalar()
        or 0
    )

    # Saved count
    saved_count = (
        db.query(func.count(Application.id))
        .filter(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.SAVED,
        )
        .scalar()
        or 0
    )

    # Applied count
    applied_count = (
        db.query(func.count(Application.id))
        .filter(
            Application.user_id == user_id,
            Application.status == ApplicationStatus.APPLIED,
        )
        .scalar()
        or 0
    )

    # Recent runs
    service = PipelineService(db)
    recent_runs = service.get_pipeline_history(user_id=user_id, limit=5)

    return StatsOverviewResponse(
        total_jobs=total_jobs,
        total_applications=total_applications,
        saved_count=saved_count,
        applied_count=applied_count,
        recent_runs=recent_runs,
    )


@router.get("/by-category", response_model=List[CategoryStatsResponse])
def get_category_stats(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    """Get job count by category."""
    stats = (
        db.query(Job.category, func.count(Job.id).label("count"))
        .filter(Job.category.isnot(None))
        .group_by(Job.category)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    return [
        CategoryStatsResponse(category=cat, count=count) for cat, count in stats
    ]


@router.get("/by-source", response_model=List[SourceStatsResponse])
def get_source_stats(
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
):
    """Get job count by source."""
    stats = (
        db.query(Job.source, func.count(Job.id).label("count"))
        .filter(Job.source.isnot(None))
        .group_by(Job.source)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    return [SourceStatsResponse(source=src, count=count) for src, count in stats]


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get complete analytics dashboard data."""
    overview = get_overview(db, user_id)
    by_category = get_category_stats(db, user_id)
    by_source = get_source_stats(db, user_id)

    return AnalyticsResponse(
        overview=overview,
        by_category=by_category,
        by_source=by_source,
    )
