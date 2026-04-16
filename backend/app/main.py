"""
FastAPI main application - orchestrates all API routes and middleware.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    # Startup
    logger.info("Starting up FastAPI application...")
    try:
        # Import and init DB
        from backend.app.db.database import init_db
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}", exc_info=True)
        # Continue anyway - might be first startup

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")


# Create FastAPI app
app = FastAPI(
    title="Job Recommendation SaaS API",
    description="AI-powered job recommendation platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware - allow frontend to access API
import os
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Backend API is running"}


# Import routers AFTER app creation to avoid circular imports
try:
    from backend.app.api import jobs, applications, pipeline, stats, auth
    app.include_router(auth.router)
    app.include_router(jobs.router)
    app.include_router(applications.router)
    app.include_router(pipeline.router)
    app.include_router(stats.router)
    logger.info("✓ All API routers loaded successfully")
except Exception as e:
    logger.error(f"✗ Failed to load API routers: {e}", exc_info=True)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
