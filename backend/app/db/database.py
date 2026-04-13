"""
Database connection and configuration for PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - supports both Docker and local
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://job_user:job_password@postgres:5432/job_recommendations"
)

# Create base class for ORM models
Base = declarative_base()

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for FastAPI to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    # Import models here to avoid circular imports
    from backend.app.models.models import User, Job, Application, PipelineRun, UserPreferences
    Base.metadata.create_all(bind=engine)
