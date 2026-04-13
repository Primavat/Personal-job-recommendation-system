"""
Job service - handles job queries, filtering, and user interactions.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Tuple
from backend.app.models.models import Job, Application, ApplicationStatus
from backend.app.db.schemas import JobDetailResponse, ApplicationWithJobResponse, ApplicationResponse


class JobService:
    """Service for job-related operations."""

    def __init__(self, db: Session):
        self.db = db

    def search_jobs(
        self,
        user_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Tuple[List[JobDetailResponse], int]:
        """
        Search and filter jobs with pagination.

        Returns:
            Tuple of (jobs, total_count)
        """
        query = self.db.query(Job)

        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Job.title.ilike(search_term),
                    Job.description.ilike(search_term),
                    Job.company.ilike(search_term),
                )
            )

        if category:
            query = query.filter(Job.category == category)

        if location:
            location_term = f"%{location}%"
            query = query.filter(Job.location.ilike(location_term))

        if job_type:
            query = query.filter(Job.job_type == job_type)

        if source:
            query = query.filter(Job.source == source)

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        jobs = query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()

        # Enrich with user application status
        result = []
        for job in jobs:
            job_detail = JobDetailResponse.model_validate(job)
            if user_id:
                app = (
                    self.db.query(Application)
                    .filter(
                        and_(
                            Application.user_id == user_id,
                            Application.job_id == job.id,
                        )
                    )
                    .first()
                )
                if app:
                    job_detail.user_application_status = app.status
                    job_detail.user_notes = app.notes
            result.append(job_detail)

        return result, total_count

    def get_job(self, job_id: str, user_id: Optional[str] = None) -> Optional[JobDetailResponse]:
        """Get a single job with user's application status."""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        job_detail = JobDetailResponse.model_validate(job)
        if user_id:
            app = (
                self.db.query(Application)
                .filter(
                    and_(
                        Application.user_id == user_id,
                        Application.job_id == job.id,
                    )
                )
                .first()
            )
            if app:
                job_detail.user_application_status = app.status
                job_detail.user_notes = app.notes

        return job_detail

    def get_categories(self) -> List[str]:
        """Get all unique job categories."""
        categories = (
            self.db.query(Job.category)
            .distinct()
            .order_by(Job.category)
            .all()
        )
        return [cat[0] for cat in categories if cat[0]]

    def get_sources(self) -> List[str]:
        """Get all unique job sources."""
        sources = (
            self.db.query(Job.source)
            .distinct()
            .order_by(Job.source)
            .all()
        )
        return [src[0] for src in sources if src[0]]

    def get_locations(self) -> List[str]:
        """Get all unique job locations."""
        locations = (
            self.db.query(Job.location)
            .distinct()
            .order_by(Job.location)
            .all()
        )
        return [loc[0] for loc in locations if loc[0]]


class ApplicationService:
    """Service for user application tracking."""

    def __init__(self, db: Session):
        self.db = db

    def save_job(
        self, user_id: str, job_id: str, notes: Optional[str] = None
    ) -> ApplicationResponse:
        """Save a job for later."""
        # Check if already saved
        existing = (
            self.db.query(Application)
            .filter(
                and_(
                    Application.user_id == user_id,
                    Application.job_id == job_id,
                )
            )
            .first()
        )

        if existing:
            # Update notes if provided
            if notes:
                existing.notes = notes
            self.db.commit()
            self.db.refresh(existing)
            return ApplicationResponse.model_validate(existing)

        # Create new saved job
        app = Application(
            user_id=user_id,
            job_id=job_id,
            status=ApplicationStatus.SAVED,
            notes=notes,
        )
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        return ApplicationResponse.model_validate(app)

    def unsave_job(self, user_id: str, job_id: str) -> bool:
        """Remove saved job."""
        app = (
            self.db.query(Application)
            .filter(
                and_(
                    Application.user_id == user_id,
                    Application.job_id == job_id,
                )
            )
            .first()
        )
        if app:
            self.db.delete(app)
            self.db.commit()
            return True
        return False

    def update_application(
        self,
        user_id: str,
        job_id: str,
        status: ApplicationStatus,
        notes: Optional[str] = None,
    ) -> ApplicationResponse:
        """Update application status."""
        app = (
            self.db.query(Application)
            .filter(
                and_(
                    Application.user_id == user_id,
                    Application.job_id == job_id,
                )
            )
            .first()
        )

        if not app:
            # Create if doesn't exist
            app = Application(
                user_id=user_id,
                job_id=job_id,
                status=status,
                notes=notes,
            )
            self.db.add(app)
        else:
            app.status = status
            if notes is not None:
                app.notes = notes

        self.db.commit()
        self.db.refresh(app)
        return ApplicationResponse.model_validate(app)

    def get_user_applications(
        self,
        user_id: str,
        status: Optional[ApplicationStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[ApplicationWithJobResponse], int]:
        """Get user's saved/applied jobs."""
        query = self.db.query(Application).filter(Application.user_id == user_id)

        if status:
            query = query.filter(Application.status == status)

        total_count = query.count()

        offset = (page - 1) * limit
        apps = (
            query.order_by(Application.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        result = []
        for app in apps:
            job = self.db.query(Job).filter(Job.id == app.job_id).first()
            app_with_job = ApplicationWithJobResponse(
                **ApplicationResponse.model_validate(app).model_dump(),
                job=job,
            )
            result.append(app_with_job)

        return result, total_count

    def get_application(
        self, user_id: str, job_id: str
    ) -> Optional[ApplicationResponse]:
        """Get user's application for a specific job."""
        app = (
            self.db.query(Application)
            .filter(
                and_(
                    Application.user_id == user_id,
                    Application.job_id == job_id,
                )
            )
            .first()
        )
        return ApplicationResponse.model_validate(app) if app else None
