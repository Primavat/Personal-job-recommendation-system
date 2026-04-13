"""
API endpoints for job operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.database import get_db
from backend.app.auth import get_current_user
from backend.app.db.schemas import JobDetailResponse, JobResponse
from backend.app.services.job_service import JobService

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=dict)
def list_jobs(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    """
    List all jobs with optional filtering and pagination.

    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    - search: Search in title/description/company
    - category: Filter by category (e.g., "AI / ML")
    - location: Filter by location
    - job_type: Filter by type (Internship, Full-time, etc.)
    - source: Filter by source (Remotive, Arbeitnow, etc.)
    """
    service = JobService(db)
    jobs, total = service.search_jobs(
        user_id=user_id,
        page=page,
        limit=limit,
        search=search,
        category=category,
        location=location,
        job_type=job_type,
        source=source,
    )
    return {
        "items": jobs,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/filters/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    """Get all available job categories."""
    service = JobService(db)
    return service.get_categories()


@router.get("/filters/sources", response_model=List[str])
def get_sources(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    """Get all available job sources."""
    service = JobService(db)
    return service.get_sources()


@router.get("/filters/locations", response_model=List[str])
def get_locations(db: Session = Depends(get_db), _: str = Depends(get_current_user)):
    """Get all available job locations."""
    service = JobService(db)
    return service.get_locations()


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get detailed information about a specific job."""
    service = JobService(db)
    job = service.get_job(job_id, user_id=user_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
