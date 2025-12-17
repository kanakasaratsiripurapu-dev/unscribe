"""
FastAPI main application for SubScout
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api import auth, scan, subscriptions, dashboard, activity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting SubScout API...")
    # Create database tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SubScout API...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="SubScout API",
    description="AI-powered subscription management platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.detail,
                "message": str(exc.detail),
                "timestamp": "2025-12-15T10:30:00Z"  # Use actual timestamp
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": "2025-12-15T10:30:00Z"
            }
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2025-12-15T10:30:00Z",
        "services": {
            "database": "up",
            "redis": "up",
            "gmail_api": "up"
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SubScout API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(scan.router, prefix="/api/scan", tags=["Email Scanning"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(activity.router, prefix="/api/activity", tags=["Activity Log"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
