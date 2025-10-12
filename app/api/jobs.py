from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from app.services.webhook_processor import WebhookProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{job_id}/status")
async def get_job_status(job_id: str):
    """
    Get the status of a video generation job
    """
    try:
        processor = WebhookProcessor()
        job_data = processor.get_job_status(job_id)
        
        if not job_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Job {job_id} not found"
            )
        
        return {
            "job_id": job_id,
            "status": job_data.get("status"),
            "created_at": job_data.get("created_at"),
            "completed_at": job_data.get("completed_at"),
            "video_url": job_data.get("video_url"),
            "error_message": job_data.get("error_message")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving job status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{job_id}/video")
async def get_job_video(job_id: str):
    """
    Get the video URL for a completed job
    """
    try:
        processor = WebhookProcessor()
        job_data = processor.get_job_status(job_id)
        
        if not job_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Job {job_id} not found"
            )
        
        status = job_data.get("status")
        
        if status == "completed":
            video_url = job_data.get("video_url")
            if video_url:
                return {
                    "job_id": job_id,
                    "video_url": video_url,
                    "status": "ready"
                }
        elif status == "processing":
            return {
                "job_id": job_id,
                "status": "processing",
                "message": "Video is still being generated"
            }
        elif status == "failed":
            return {
                "job_id": job_id,
                "status": "failed",
                "error": job_data.get("error_message")
            }
        else:
            return {
                "job_id": job_id,
                "status": status
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving video: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")