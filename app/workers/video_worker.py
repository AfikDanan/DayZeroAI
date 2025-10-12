import logging
from datetime import datetime
from redis import Redis
from app.models.webhook import EmployeeData
from app.services.video_generator import VideoGenerator
from app.services.notification_service import NotificationService
from app.config import settings

logger = logging.getLogger(__name__)

def generate_onboarding_video(employee_data_dict: dict, job_id: str) -> dict:
    """
    Background worker function for video generation
    This runs in RQ worker process
    """
    redis_conn = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    
    try:
        # Update job status to processing
        _update_job_status(redis_conn, job_id, "processing")
        
        logger.info(f"Starting video generation for job {job_id}")
        
        # Convert dict back to EmployeeData model
        employee_data = EmployeeData(**employee_data_dict)
        
        # Generate video
        video_gen = VideoGenerator()
        video_path = video_gen.generate_onboarding_video(
            employee_data, 
            job_id
        )
        
        # In MVP, video_url is just the filename
        ### TODO: In production, this would be S3 URL
        video_url = f"/videos/{job_id}.mp4"
        
        # Update job status to completed
        _update_job_status(
            redis_conn, 
            job_id, 
            "completed",
            video_url=video_url
        )
        
        # Send notification to new hire
        notification_service = NotificationService()
        notification_service.send_video_ready_email(
            employee_data.email,
            employee_data.name,
            video_url
        )
        
        logger.info(f"Video generation completed for job {job_id}")
        
        return {
            "success": True,
            "job_id": job_id,
            "video_url": video_url
        }
        
    except Exception as e:
        logger.error(f"Error in video generation for job {job_id}: {str(e)}")
        
        # Update job status to failed
        _update_job_status(
            redis_conn, 
            job_id, 
            "failed",
            error_message=str(e)
        )
        
        raise

def _update_job_status(
    redis_conn: Redis,
    job_id: str,
    status: str,
    video_url: str = None,
    error_message: str = None
) -> None:
    """Update job status in Redis"""
    key = f"job:{job_id}"
    
    updates = {
        "status": status,
        "updated_at": datetime.now().isoformat()
    }
    
    if status == "completed":
        updates["completed_at"] = datetime.now().isoformat()
        if video_url:
            updates["video_url"] = video_url
    
    if error_message:
        updates["error_message"] = error_message
    
    redis_conn.hset(key, mapping=updates)