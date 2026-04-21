"""
Database models (SQLAlchemy ORM) for the job recommendation system.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
import enum
from backend.app.db.database import Base


class User(Base):
    """User account (managed via Supabase Auth, this is for reference)."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # UUID from Supabase
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    pipeline_runs = relationship("PipelineRun", back_populates="user", cascade="all, delete-orphan")


class Job(Base):
    """Job listings from aggregated sources."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)  # SHA1 hash from collector
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)
    job_type = Column(String)  # Internship, Full-time, Part-time, Contract, Freelance
    category = Column(String, index=True)  # AI/ML, Frontend, Backend, etc.
    description = Column(Text)
    ai_summary = Column(Text)
    source = Column(String)  # Remotive, Arbeitnow, The Muse, FindWork
    apply_link = Column(String)
    tags = Column(String)  # Comma-separated
    date_posted = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")


class ApplicationStatus(str, enum.Enum):
    """Status of user's interest in a job."""
    SAVED = "saved"
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEWED = "interviewed"
    OFFERED = "offered"


class Application(Base):
    """User's application tracking for jobs."""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    job_id = Column(String, ForeignKey("jobs.id"), index=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SAVED, index=True)
    notes = Column(Text, nullable=True)
    applied_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class PipelineRunStatus(str, enum.Enum):
    """Status of pipeline execution."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineRun(Base):
    """Track history of pipeline executions."""
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
    status = Column(Enum(PipelineRunStatus), default=PipelineRunStatus.RUNNING)
    jobs_collected = Column(Integer, default=0)
    jobs_processed = Column(Integer, default=0)
    jobs_added = Column(Integer, default=0)
    error_log = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="pipeline_runs")


class UserPreferences(Base):
    """User configuration and preferences."""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, index=True)

    # Pipeline scheduling
    pipeline_enabled = Column(Boolean, default=True)
    pipeline_interval_hours = Column(Integer, default=6)  # Run every N hours

    # Job filters
    preferred_locations = Column(String, nullable=True)  # JSON list
    preferred_categories = Column(String, nullable=True)  # JSON list
    job_types_filter = Column(String, nullable=True)  # JSON list

    # Notifications
    telegram_enabled = Column(Boolean, default=False)
    telegram_chat_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
