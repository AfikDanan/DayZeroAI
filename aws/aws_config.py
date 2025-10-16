#!/usr/bin/env python3
"""
AWS Configuration for Production Deployment
This file has been moved to aws/config.py
"""

# This file has been moved to aws/config.py
# Please update your imports to: from aws.config import aws_settings

print("⚠️  This file has been moved to aws/config.py")
print("💡 Please update imports to: from aws.config import aws_settings")
exit(1)

from pydantic_settings import BaseSettings
from typing import Optional

class AWSSettings(BaseSettings):
    """AWS-specific configuration settings"""
    
    # AWS General
    AWS_REGION: str = "us-east-1"
    AWS_ACCOUNT_ID: Optional[str] = None
    
    # S3 Configuration
    S3_BUCKET_NAME: str = "preboarding-videos"
    S3_BUCKET_REGION: str = "us-east-1"
    S3_VIDEO_PREFIX: str = "videos/"
    S3_DEV_PREFIX: str = "dev-output/"
    
    # Lambda Configuration
    LAMBDA_FUNCTION_NAME: str = "preboarding-api"
    LAMBDA_WORKER_FUNCTION_NAME: str = "preboarding-worker"
    LAMBDA_TIMEOUT: int = 900  # 15 minutes max for video generation
    LAMBDA_MEMORY: int = 3008  # Max memory for video processing
    
    # ElastiCache Redis
    REDIS_CLUSTER_ENDPOINT: Optional[str] = None
    REDIS_PORT: int = 6379
    
    # SES Configuration (Alternative to SendGrid)
    SES_FROM_EMAIL: Optional[str] = None
    SES_REGION: str = "us-east-1"
    
    # CloudWatch
    LOG_GROUP_NAME: str = "/aws/lambda/preboarding"
    
    # API Gateway
    API_GATEWAY_STAGE: str = "prod"
    API_GATEWAY_DOMAIN: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "production"
    
    class Config:
        env_file = ".env.aws"
        case_sensitive = True

aws_settings = AWSSettings()