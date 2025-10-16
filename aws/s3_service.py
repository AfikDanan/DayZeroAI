#!/usr/bin/env python3
"""
AWS S3 Service for file storage and management
"""

import boto3
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from aws_config import aws_settings

logger = logging.getLogger(__name__)

class S3Service:
    """AWS S3 service for video and file storage"""
    
    def __init__(self):
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=aws_settings.S3_BUCKET_REGION
            )
            self.bucket_name = aws_settings.S3_BUCKET_NAME
            
            # Test S3 connection
            self._test_connection()
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {e}")
            raise
    
    def _test_connection(self) -> bool:
        """Test S3 connection and bucket access"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 connection successful to bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"S3 bucket {self.bucket_name} does not exist")
            elif error_code == '403':
                logger.error(f"Access denied to S3 bucket {self.bucket_name}")
            else:
                logger.error(f"S3 connection error: {e}")
            raise
    
    def upload_video(
        self, 
        local_path: Path, 
        job_id: str,
        content_type: str = "video/mp4"
    ) -> str:
        """Upload video file to S3 and return public URL"""
        
        s3_key = f"{aws_settings.S3_VIDEO_PREFIX}{job_id}.mp4"
        
        try:
            # Upload with metadata
            extra_args = {
                'ContentType': content_type,
                'Metadata': {
                    'job_id': job_id,
                    'upload_timestamp': str(int(time.time())),
                    'service': 'preboarding-video-generator'
                }
            }
            
            self.s3_client.upload_file(
                str(local_path),
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Generate public URL
            video_url = f"https://{self.bucket_name}.s3.{aws_settings.S3_BUCKET_REGION}.amazonaws.com/{s3_key}"
            
            logger.info(f"Video uploaded successfully: {video_url}")
            return video_url
            
        except Exception as e:
            logger.error(f"Failed to upload video {job_id}: {e}")
            raise
    
    def upload_dev_files(
        self, 
        dev_dir: Path, 
        job_id: str
    ) -> Dict[str, str]:
        """Upload development files to S3 for debugging"""
        
        uploaded_files = {}
        s3_prefix = f"{aws_settings.S3_DEV_PREFIX}{job_id}/"
        
        try:
            # Upload all files in dev directory
            for file_path in dev_dir.rglob("*"):
                if file_path.is_file():
                    # Calculate relative path for S3 key
                    relative_path = file_path.relative_to(dev_dir)
                    s3_key = f"{s3_prefix}{relative_path}"
                    
                    # Determine content type
                    content_type = self._get_content_type(file_path.suffix)
                    
                    self.s3_client.upload_file(
                        str(file_path),
                        self.bucket_name,
                        s3_key,
                        ExtraArgs={'ContentType': content_type}
                    )
                    
                    file_url = f"https://{self.bucket_name}.s3.{aws_settings.S3_BUCKET_REGION}.amazonaws.com/{s3_key}"
                    uploaded_files[str(relative_path)] = file_url
            
            logger.info(f"Uploaded {len(uploaded_files)} dev files for job {job_id}")
            return uploaded_files
            
        except Exception as e:
            logger.error(f"Failed to upload dev files for {job_id}: {e}")
            raise
    
    def generate_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 3600
    ) -> str:
        """Generate presigned URL for temporary access"""
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    def delete_video(self, job_id: str) -> bool:
        """Delete video from S3"""
        
        s3_key = f"{aws_settings.S3_VIDEO_PREFIX}{job_id}.mp4"
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Video deleted: {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete video {job_id}: {e}")
            return False
    
    def list_videos(self, limit: int = 100) -> list:
        """List videos in S3 bucket"""
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=aws_settings.S3_VIDEO_PREFIX,
                MaxKeys=limit
            )
            
            videos = []
            for obj in response.get('Contents', []):
                videos.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'url': f"https://{self.bucket_name}.s3.{aws_settings.S3_BUCKET_REGION}.amazonaws.com/{obj['Key']}"
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"Failed to list videos: {e}")
            return []
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension"""
        
        content_types = {
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.html': 'text/html'
        }
        
        return content_types.get(file_extension.lower(), 'application/octet-stream')
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """Get S3 bucket information"""
        
        try:
            # Get bucket location
            location = self.s3_client.get_bucket_location(
                Bucket=self.bucket_name
            )
            
            # Get bucket size (approximate)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name
            )
            
            total_size = sum(obj['Size'] for obj in response.get('Contents', []))
            object_count = len(response.get('Contents', []))
            
            return {
                'bucket_name': self.bucket_name,
                'region': location.get('LocationConstraint', 'us-east-1'),
                'object_count': object_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get bucket info: {e}")
            return {}

# Import time for metadata
import time