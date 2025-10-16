#!/usr/bin/env python3
"""
AWS-optimized video worker for Lambda environment
"""

import logging
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from app.models.webhook import EmployeeData
from app.services.video_generator import VideoGenerator
from app.services.notification_service import NotificationService
from aws.s3_service import S3Service
from aws_config import aws_settings

logger = logging.getLogger(__name__)

def generate_onboarding_video_aws(employee_data_dict: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """
    AWS Lambda optimized video generation function
    Uses S3 for storage instead of local filesystem
    """
    
    try:
        logger.info(f"Starting AWS video generation for job {job_id}")
        
        # Convert dict to EmployeeData model
        employee_data = EmployeeData(**employee_data_dict)
        
        # Create temporary directories for Lambda
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            work_dir = temp_path / job_id
            work_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize services
            video_gen = VideoGenerator()
            s3_service = S3Service()
            notification_service = NotificationService()
            
            # Override video generator paths for Lambda
            video_gen.temp_dir = temp_path
            video_gen.output_dir = work_dir
            
            logger.info("Generating video with AWS-optimized settings...")
            
            # Generate video (this creates local files in temp directory)
            local_video_path = video_gen.generate_onboarding_video(
                employee_data, 
                job_id
            )
            
            logger.info(f"Video generated locally: {local_video_path}")
            
            # Upload video to S3
            logger.info("Uploading video to S3...")
            s3_video_url = s3_service.upload_video(
                local_video_path,
                job_id
            )
            
            # Upload development files to S3 (for debugging)
            dev_dir = temp_path / "dev_output" / job_id
            if dev_dir.exists():
                logger.info("Uploading development files to S3...")
                dev_files = s3_service.upload_dev_files(dev_dir, job_id)
                logger.info(f"Uploaded {len(dev_files)} development files")
            
            # Send notification with S3 URL
            logger.info("Sending notification email...")
            
            # Try to send email notification
            email_sent = notification_service.send_video_ready_email(
                employee_data.email,
                employee_data.name,
                s3_video_url  # Use S3 URL instead of local path
            )
            
            if not email_sent:
                logger.warning("Email notification failed, using fallback")
                notification_service.send_video_ready_email(
                    employee_data.email,
                    employee_data.name,
                    s3_video_url,
                    use_fallback=True
                )
            
            logger.info(f"AWS video generation completed for job {job_id}")
            
            return {
                "success": True,
                "job_id": job_id,
                "video_url": s3_video_url,
                "storage": "s3",
                "bucket": aws_settings.S3_BUCKET_NAME,
                "environment": "aws_lambda"
            }
    
    except Exception as e:
        logger.error(f"AWS video generation failed for job {job_id}: {str(e)}")
        
        # Send error notification
        try:
            notification_service = NotificationService()
            notification_service.send_error_notification(
                employee_data.email,
                employee_data.name,
                str(e)
            )
        except Exception as notification_error:
            logger.error(f"Failed to send error notification: {notification_error}")
        
        raise

def cleanup_lambda_temp_files(temp_dir: Path) -> None:
    """Clean up temporary files in Lambda environment"""
    
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp files: {e}")

def get_lambda_environment_info() -> Dict[str, Any]:
    """Get Lambda environment information for debugging"""
    
    import os
    
    return {
        "aws_region": os.getenv("AWS_REGION"),
        "lambda_function_name": os.getenv("AWS_LAMBDA_FUNCTION_NAME"),
        "lambda_function_version": os.getenv("AWS_LAMBDA_FUNCTION_VERSION"),
        "lambda_memory_size": os.getenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE"),
        "lambda_timeout": os.getenv("AWS_LAMBDA_FUNCTION_TIMEOUT"),
        "temp_dir": "/tmp",
        "available_disk_space": get_available_disk_space("/tmp")
    }

def get_available_disk_space(path: str) -> str:
    """Get available disk space in Lambda /tmp directory"""
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        
        return {
            "total_mb": round(total / (1024 * 1024), 2),
            "used_mb": round(used / (1024 * 1024), 2),
            "free_mb": round(free / (1024 * 1024), 2)
        }
    except Exception:
        return "unknown"