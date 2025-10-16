# app/services/webhook_processor.py
import logging
import uuid
from datetime import datetime
from typing import Optional
from redis import Redis
from rq import Queue

from app.models.webhook import (
    WebhookPayload, 
    UserOnboardingWebhook, 
    VideoGenerationJob
)
from app.services.video_generator import VideoGenerator
from app.config import settings

logger = logging.getLogger(__name__)

class WebhookProcessor:
    def __init__(self):
        self.redis_conn = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=False
        )
        self.queue = Queue('video_generation', connection=self.redis_conn)
        
    def process_generic_webhook(self, payload: WebhookPayload) -> None:
        """Process generic webhook - can be extended for other event types"""
        logger.info(f"Processing generic webhook: {payload.event_type}")
        
        # Route to appropriate handler based on event_type
        handlers = {
            'user.onboarding': self._handle_onboarding,
            'user.offboarding': self._handle_offboarding,
            
        }
        
        handler = handlers.get(payload.event_type)
        if handler:
            handler(payload.data)
        else:
            logger.warning(f"No handler for event type: {payload.event_type}")
    
    def process_user_onboarding_webhook(
        self, 
        payload: UserOnboardingWebhook
    ) -> Optional[str]:
        """Process user onboarding webhook and queue video generation"""
        try:
            job_id = str(uuid.uuid4())
            logger.info(f"Generated job_id: {job_id}")
            
            # Create job record
            job = VideoGenerationJob(
                job_id=job_id,
                employee_id=payload.employee_data.employee_id,
                status="queued",
                created_at=datetime.now()
            )
            
            # Store job info in Redis
            self._store_job(job)
            logger.info(f"Stored job in Redis: {job_id}")
            
            # Queue the video generation job
            from app.workers.video_worker import generate_onboarding_video
            rq_job = self.queue.enqueue(
                generate_onboarding_video,
                payload.employee_data.model_dump(),
                job_id=job_id,
                timeout='10m',
                result_ttl=86400  # Keep result for 24 hours
            )
            
            logger.info(
                f"Queued video generation job {job_id} (RQ job: {rq_job.id}) "
                f"for employee {payload.employee_data.employee_id}"
            )
            
            return job_id
            
        except Exception as e:
            logger.error(f"Error queueing video generation: {str(e)}")
            logger.exception("Full traceback:")
            return None
    
    def _handle_onboarding(self, data: dict) -> None:
        """Handle onboarding event from generic webhook"""
        # Convert to EmployeeData and process
        logger.info(f"Handling onboarding for: {data.get('name')}")
        ###TODO: Implementation here
    
    def _handle_offboarding(self, data: dict) -> None:
        """Handle offboarding event (future feature)"""
        logger.info(f"Handling offboarding for: {data.get('name')}")
        ###TODO: Implementation here
    
    def _store_job(self, job: VideoGenerationJob) -> None:
        """Store job information in Redis"""
        redis_key = f"job:{job.job_id}"
        job_data = job.model_dump()
        
        # Convert values for Redis storage
        redis_data = {}
        for key_name, value in job_data.items():
            if value is None:
                redis_data[key_name] = ""  # Store empty string instead of None
            elif hasattr(value, 'isoformat'):  # datetime object
                redis_data[key_name] = value.isoformat()
            else:
                redis_data[key_name] = str(value)  # Convert everything to string
        
        self.redis_conn.hset(redis_key, mapping=redis_data)
        self.redis_conn.expire(redis_key, 86400)  # 24 hour TTL
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Retrieve job status from Redis"""
        key = f"job:{job_id}"
        job_data = self.redis_conn.hgetall(key)
        return job_data if job_data else None