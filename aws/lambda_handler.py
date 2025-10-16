#!/usr/bin/env python3
"""
AWS Lambda handlers for the preboarding service
"""

import json
import logging
import os
from typing import Dict, Any
from datetime import datetime

# Configure logging for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def api_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for API Gateway requests
    Handles webhook endpoints
    """
    
    try:
        # Parse the request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        body = event.get('body', '{}')
        
        logger.info(f"API Request: {http_method} {path}")
        
        # Parse JSON body if present
        if body:
            try:
                request_data = json.loads(body)
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }
        else:
            request_data = {}
        
        # Route the request
        if path == '/webhooks/user-onboarding' and http_method == 'POST':
            return handle_user_onboarding_webhook(request_data)
        elif path == '/health' and http_method == 'GET':
            return handle_health_check()
        elif path == '/' and http_method == 'GET':
            return handle_root()
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Not Found'})
            }
    
    except Exception as e:
        logger.error(f"API Handler Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal Server Error'})
        }

def handle_user_onboarding_webhook(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle user onboarding webhook"""
    
    try:
        from app.models.webhook import UserOnboardingWebhook
        from app.services.webhook_processor import WebhookProcessor
        
        # Validate webhook payload
        webhook = UserOnboardingWebhook(**request_data)
        
        # Process webhook
        processor = WebhookProcessor()
        job_id = processor.process_user_onboarding_webhook(webhook)
        
        if job_id:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'message': f'User onboarding webhook processed: {webhook.event_type}',
                    'job_id': job_id,
                    'processed_at': datetime.now().isoformat()
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to process webhook'
                })
            }
    
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'message': f'Webhook validation error: {str(e)}'
            })
        }

def handle_health_check() -> Dict[str, Any]:
    """Handle health check endpoint"""
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'healthy',
            'service': 'preboarding-service',
            'timestamp': datetime.now().isoformat(),
            'environment': os.getenv('ENVIRONMENT', 'production')
        })
    }

def handle_root() -> Dict[str, Any]:
    """Handle root endpoint"""
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'service': 'Preboarding Video Service',
            'version': '1.0.0',
            'status': 'operational',
            'environment': os.getenv('ENVIRONMENT', 'production')
        })
    }

def worker_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for background video generation
    Triggered by SQS or direct invocation
    """
    
    try:
        logger.info("Worker Lambda started")
        
        # Parse the event (could be SQS, direct invocation, etc.)
        if 'Records' in event:
            # SQS event
            for record in event['Records']:
                if record.get('eventSource') == 'aws:sqs':
                    message_body = json.loads(record['body'])
                    process_video_generation_job(message_body)
        else:
            # Direct invocation
            process_video_generation_job(event)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Worker completed successfully'
            })
        }
    
    except Exception as e:
        logger.error(f"Worker Handler Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

def process_video_generation_job(job_data: Dict[str, Any]) -> None:
    """Process video generation job"""
    
    try:
        from app.workers.video_worker_aws import generate_onboarding_video_aws
        
        employee_data = job_data.get('employee_data')
        job_id = job_data.get('job_id')
        
        if not employee_data or not job_id:
            raise ValueError("Missing employee_data or job_id in job")
        
        logger.info(f"Processing video generation for job: {job_id}")
        
        # Generate video using AWS-optimized worker
        result = generate_onboarding_video_aws(employee_data, job_id)
        
        logger.info(f"Video generation completed: {result}")
        
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        raise

# Lambda function aliases for deployment
lambda_handler = api_handler  # Default handler for API Gateway
worker_lambda_handler = worker_handler  # Handler for worker Lambda