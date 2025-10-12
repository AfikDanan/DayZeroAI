from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import logging

from app.models.webhook import WebhookPayload, UserOnboardingWebhook, WebhookResponse
from app.services.webhook_processor import WebhookProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generic", response_model=WebhookResponse)
async def receive_generic_webhook(
    payload: WebhookPayload,
    background_tasks: BackgroundTasks
):
    """
    Generic webhook endpoint that can handle any webhook payload
    """
    try:
        processor = WebhookProcessor()
        
        # Process webhook in background
        background_tasks.add_task(
            processor.process_generic_webhook, 
            payload
        )
        
        return WebhookResponse(
            success=True,
            message=f"Webhook received and queued for processing: {payload.event_type}",
            processed_at=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/user-onboarding", response_model=WebhookResponse)
async def receive_user_onboarding_webhook(
    payload: UserOnboardingWebhook,
    background_tasks: BackgroundTasks
):
    """
    Specific webhook endpoint for user onboarding events
    """
    try:
        processor = WebhookProcessor()
        
        # Process user onboarding webhook and get job_id
        job_id = processor.process_user_onboarding_webhook(payload)
        
        return WebhookResponse(
            success=True,
            message=f"User onboarding webhook processed: {payload.event_type}",
            job_id=job_id,
            processed_at=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error processing user onboarding webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status")
async def webhook_status():
    """
    Check webhook service status
    """
    return {
        "status": "active",
        "endpoints": [
            "/webhooks/generic",
            "/webhooks/user-onboarding"
        ],
        "timestamp": datetime.now()
    }