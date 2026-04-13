"""
API endpoints for user application tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from backend.app.db.database import get_db
from backend.app.auth import get_current_user
from backend.app.db.schemas import (
    ApplicationResponse,
    ApplicationWithJobResponse,
    ApplicationUpdate,
    ApplicationStatusEnum,
)
from backend.app.models.models import ApplicationStatus
from backend.app.services.job_service import ApplicationService

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=dict)
def list_applications(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    status: Optional[ApplicationStatusEnum] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get user's saved/applied jobs.

    Query Parameters:
    - status: Filter by status (saved, applied, rejected, interviewed, offered)
    - page: Page number
    - limit: Items per page
    """
    service = ApplicationService(db)
    status_enum = ApplicationStatus(status) if status else None
    apps, total = service.get_user_applications(
        user_id=user_id,
        status=status_enum,
        page=page,
        limit=limit,
    )
    return {
        "items": apps,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.post("/{job_id}/save", response_model=ApplicationResponse)
def save_job(
    job_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Save a job for later."""
    service = ApplicationService(db)
    return service.save_job(user_id=user_id, job_id=job_id)


@router.delete("/{job_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(
    job_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Remove a saved job."""
    service = ApplicationService(db)
    success = service.unsave_job(user_id=user_id, job_id=job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return None


@router.patch("/{job_id}", response_model=ApplicationResponse)
def update_application(
    job_id: str,
    update: ApplicationUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Update application status and notes."""
    service = ApplicationService(db)

    # Convert string status to enum
    status_enum = (
        ApplicationStatus(update.status) if update.status else ApplicationStatus.SAVED
    )

    return service.update_application(
        user_id=user_id,
        job_id=job_id,
        status=status_enum,
        notes=update.notes,
    )


@router.get("/{job_id}", response_model=ApplicationResponse)
def get_application(
    job_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get user's application for a specific job."""
    service = ApplicationService(db)
    app = service.get_application(user_id=user_id, job_id=job_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return app
