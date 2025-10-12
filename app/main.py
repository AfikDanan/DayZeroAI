from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from app.api.webhooks import router as webhook_router
from app.api.jobs import router as jobs_router
from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="Preboarding Service",
    description="AI-powered onboarding video generation service",
    version="1.0.0"
)

# Include routers
app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])

# Serve static video files
video_dir = Path(settings.OUTPUT_DIR)
video_dir.mkdir(parents=True, exist_ok=True)
app.mount("/videos", StaticFiles(directory=str(video_dir)), name="videos")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Preboarding Video Service",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "preboarding-service"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)