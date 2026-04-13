"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ApplicationStatusEnum(str, Enum):
    SAVED = "saved"
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEWED = "interviewed"
    OFFERED = "offered"


# ── User Schemas ──────────────────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Job Schemas ───────────────────────────────────────────────────────────
class JobBase(BaseModel):
    title: str
    company: str
    location: str
    job_type: str
    category: str
    description: Optional[str] = None
    ai_summary: Optional[str] = None
    source: str
    apply_link: str
    tags: Optional[str] = None
    date_posted: str


class JobCreate(JobBase):
    id: str


class JobResponse(JobBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    """Extended job response with user's application status."""
    user_application_status: Optional[ApplicationStatusEnum] = None
    user_notes: Optional[str] = None


# ── Application Schemas ───────────────────────────────────────────────────
class ApplicationBase(BaseModel):
    status: ApplicationStatusEnum
    notes: Optional[str] = None


class ApplicationCreate(BaseModel):
    job_id: str
    status: ApplicationStatusEnum = ApplicationStatusEnum.SAVED


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatusEnum] = None
    notes: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: int
    user_id: str
    job_id: str
    applied_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationWithJobResponse(ApplicationResponse):
    """Application with embedded job details."""
    job: JobResponse


# ── Pipeline Schemas ──────────────────────────────────────────────────────
class PipelineRunResponse(BaseModel):
    id: int
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str
    jobs_collected: int
    jobs_processed: int
    jobs_added: int
    error_log: Optional[str] = None

    class Config:
        from_attributes = True


class PipelineRunRequest(BaseModel):
    job_filter: Optional[str] = None  # "remote", "intern", or None


# ── User Preferences Schemas ──────────────────────────────────────────────
class UserPreferencesResponse(BaseModel):
    pipeline_enabled: bool
    pipeline_interval_hours: int
    preferred_locations: Optional[List[str]] = None
    preferred_categories: Optional[List[str]] = None
    job_types_filter: Optional[List[str]] = None
    telegram_enabled: bool
    telegram_chat_id: Optional[str] = None

    class Config:
        from_attributes = True


class UserPreferencesUpdate(BaseModel):
    pipeline_enabled: Optional[bool] = None
    pipeline_interval_hours: Optional[int] = None
    preferred_locations: Optional[List[str]] = None
    preferred_categories: Optional[List[str]] = None
    job_types_filter: Optional[List[str]] = None
    telegram_enabled: Optional[bool] = None
    telegram_chat_id: Optional[str] = None


# ── Analytics Schemas ─────────────────────────────────────────────────────
class StatsOverviewResponse(BaseModel):
    total_jobs: int
    total_applications: int
    saved_count: int
    applied_count: int
    recent_runs: List[PipelineRunResponse]


class CategoryStatsResponse(BaseModel):
    category: str
    count: int


class SourceStatsResponse(BaseModel):
    source: str
    count: int


class AnalyticsResponse(BaseModel):
    overview: StatsOverviewResponse
    by_category: List[CategoryStatsResponse]
    by_source: List[SourceStatsResponse]
