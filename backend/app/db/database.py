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
    """Create all tables and seed default data."""
    # Import models here to avoid circular imports
    from backend.app.models.models import User, Job, Application, PipelineRun, UserPreferences
    Base.metadata.create_all(bind=engine)
    
    # Seed default user if not exists
    db = SessionLocal()
    try:
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            import uuid
            new_user = User(id=str(uuid.uuid4()), email="test@example.com")
            db.add(new_user)
            db.commit()
    finally:
        db.close()
