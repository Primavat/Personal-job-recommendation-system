"""Seed script to create initial DB rows for local development.

Run with:
    python -m backend.app.db.seed_db

This will call backend.app.db.database.init_db() (which runs Base.metadata.create_all)
and then insert a test user and two sample jobs if they don't already exist.
"""

try:
    from backend.app.db.database import init_db, SessionLocal
    from backend.app.models.models import User, Job
    from sqlalchemy.exc import IntegrityError
except ModuleNotFoundError as e:
    missing = str(e).split("'")[-2]
    print(f"Missing dependency: {missing}.\nTo run this script locally install backend requirements: \n  pip install -r backend/requirements.txt\nOr run the seed inside Docker: \n  docker-compose exec backend python -m backend.app.db.seed_db")
    raise


def seed():
    print("Initializing database and creating tables...")
    init_db()

    db = SessionLocal()
    try:
        # Create test user
        user_id = "test-user"
        existing_user = db.query(User).filter(User.id == user_id).first()
        if not existing_user:
            print("Adding test user...")
            user = User(id=user_id, email="test@example.com")
            db.add(user)
        else:
            print("Test user already exists")

        # Create sample jobs
        samples = [
            Job(
                id="seed-job-1",
                title="Software Engineering Intern",
                company="Acme Corp",
                location="Remote",
                job_type="Internship",
                category="Frontend",
                description="An internship for students to learn frontend development.",
                ai_summary="Front-end internship role at Acme.",
                source="Seeder",
                apply_link="https://example.com/apply/1",
                tags="intern,frontend,react",
                date_posted="2026-04-13",
            ),
            Job(
                id="seed-job-2",
                title="Machine Learning Intern",
                company="DataWorks",
                location="Remote",
                job_type="Internship",
                category="AI/ML",
                description="An internship focused on ML research and model development.",
                ai_summary="ML internship at DataWorks.",
                source="Seeder",
                apply_link="https://example.com/apply/2",
                tags="intern,ml,python",
                date_posted="2026-04-12",
            ),
        ]

        added = 0
        for job in samples:
            if not db.query(Job).filter(Job.id == job.id).first():
                db.add(job)
                added += 1

        db.commit()
        print(f"Seeding complete. Added user (if missing) and {added} job(s).")
    except IntegrityError as e:
        db.rollback()
        print(f"IntegrityError during seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
