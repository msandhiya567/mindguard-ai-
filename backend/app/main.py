"""
MindGuard AI - Backend Entrypoint
====================================
Run this with:
    uvicorn app.main:app --reload

from inside the backend/ folder (not backend/app/).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
app = FastAPI(
    title="MindGuard AI API",
    description=(
        "Digital Well-Being Risk Assessment API. "
        "IMPORTANT: this system provides a risk-screening signal, "
        "not a medical diagnosis."
    ),
    version="0.1.0",
)

# CORS: allows the React frontend (running on a different port during
# development) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
from app.api import assessment
app.include_router(assessment.router)
@app.get("/health", tags=["system"])
def health_check():
    """
    Simple liveness check. Returns 200 if the API process is up.
    Does NOT check the database connection - see /health/db for that
    once the database models are wired in (Phase 4).
    """
    return {
        "status": "ok",
        "service": "mindguard-ai-backend",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["system"])
def root():
    return {
        "message": "MindGuard AI API is running.",
        "docs": "/docs",
    }