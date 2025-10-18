"""
S3 connection and storage management.
"""
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


class S3Connection:
    """Manages S3 connection and operations."""
    
    def __init__(self):
        self.client: Optional[boto3.client] = None
        self.is_connected_flag = False
        self.bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'hirethon-url-shortener')
        self.region_name = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
        self.aws_access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        self.aws_secret_access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        
    def connect(self) -> None:
        """Establish S3 connection."""
        if self.is_connected_flag and self.client:
            return
            
        try:
            # Configure S3 client
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            # Test connection by listing buckets
            self.client.list_buckets()
            self.is_connected_flag = True
            logger.info("S3 connection established")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            self.is_connected_flag = False
            raise
        except ClientError as e:
            logger.error("Failed to connect to S3: %s", e)
            self.is_connected_flag = False
            raise
        except Exception as e:
            logger.error("Unexpected error connecting to S3: %s", e)
            self.is_connected_flag = False
            raise
    
    def disconnect(self) -> None:
        """Close S3 connection."""
        if self.client:
            try:
                self.client.close()
                self.is_connected_flag = False
                logger.info("S3 connection closed")
            except Exception as e:
                logger.error("Error closing S3 connection: %s", e)
    
    def get_client(self) -> boto3.client:
        """Get S3 client instance."""
        if not self.is_connected_flag or not self.client:
            self.connect()
        return self.client
    
    def is_connected(self) -> bool:
        """Check if S3 client is connected."""
        try:
            return self.is_connected_flag and self.client is not None
        except Exception:
            return False
    
    def upload_file(self, file_path: str, s3_key: str, content_type: str = None) -> bool:
        """Upload file to S3."""
        try:
            if not self.is_connected():
                self.connect()
            
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_file(file_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            logger.info("File uploaded to S3: %s", s3_key)
            return True
            
        except Exception as e:
            logger.error("Failed to upload file to S3: %s", e)
            return False
    
    def upload_fileobj(self, file_obj, s3_key: str, content_type: str = None) -> bool:
        """Upload file object to S3."""
        try:
            if not self.is_connected():
                self.connect()
            
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_fileobj(file_obj, self.bucket_name, s3_key, ExtraArgs=extra_args)
            logger.info("File object uploaded to S3: %s", s3_key)
            return True
            
        except Exception as e:
            logger.error("Failed to upload file object to S3: %s", e)
            return False
    
    def download_file(self, s3_key: str, file_path: str) -> bool:
        """Download file from S3."""
        try:
            if not self.is_connected():
                self.connect()
            
            self.client.download_file(self.bucket_name, s3_key, file_path)
            logger.info("File downloaded from S3: %s", s3_key)
            return True
            
        except Exception as e:
            logger.error("Failed to download file from S3: %s", e)
            return False
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3."""
        try:
            if not self.is_connected():
                self.connect()
            
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info("File deleted from S3: %s", s3_key)
            return True
            
        except Exception as e:
            logger.error("Failed to delete file from S3: %s", e)
            return False
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate presigned URL for file access."""
        try:
            if not self.is_connected():
                self.connect()
            
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            logger.info("Generated presigned URL for: %s", s3_key)
            return url
            
        except Exception as e:
            logger.error("Failed to generate presigned URL: %s", e)
            return None
    
    def get_file_info(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """Get file information from S3."""
        try:
            if not self.is_connected():
                self.connect()
            
            response = self.client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return {
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag')
            }
            
        except Exception as e:
            logger.error("Failed to get file info from S3: %s", e)
            return None
