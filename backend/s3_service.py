"""
S3 Service for FARM2FORK Platform

This module provides S3 integration for uploading and managing images and QR codes.
Implements upload_file method with boto3, generates unique file keys with UUID,
returns S3 URLs for uploaded files, and configures bucket CORS for frontend access.

Requirements: 3.9, 10.5, 10.6
"""

import boto3
import uuid
import os
from typing import Optional, BinaryIO
from botocore.exceptions import ClientError
from botocore.config import Config
import logging

logger = logging.getLogger(__name__)


class S3Service:
    """Service class for AWS S3 operations"""
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize S3 service with AWS credentials and bucket configuration.
        
        Args:
            bucket_name: S3 bucket name (defaults to env var S3_BUCKET_NAME)
            region: AWS region (defaults to env var AWS_REGION)
            aws_access_key_id: AWS access key (defaults to env var)
            aws_secret_access_key: AWS secret key (defaults to env var)
        """
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET_NAME', 'farm2fork-images')
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        
        # Configure boto3 client with retry logic
        config = Config(
            region_name=self.region,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            }
        )
        
        # Initialize S3 client
        self.client = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=config
        )
        
        logger.info(f"S3Service initialized for bucket: {self.bucket_name}, region: {self.region}")
    
    def upload_file(
        self,
        file_obj: BinaryIO,
        file_type: str,
        content_type: str = 'image/jpeg',
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload a file to S3 with a unique UUID-based key.
        
        Args:
            file_obj: File object or bytes to upload
            file_type: Type of file (e.g., 'seed_packet', 'crop', 'pesticide', 'fertilizer', 'qr_code')
            content_type: MIME type of the file (default: 'image/jpeg')
            metadata: Optional metadata dictionary to attach to the file
        
        Returns:
            str: Public S3 URL of the uploaded file
        
        Raises:
            ClientError: If upload fails
        """
        try:
            # Generate unique file key with UUID
            file_key = self._generate_unique_key(file_type)
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': file_key,
                'Body': file_obj,
                'ContentType': content_type,
            }
            
            # Add metadata if provided
            if metadata:
                upload_params['Metadata'] = metadata
            
            # Try to upload with public-read ACL first
            try:
                upload_params_with_acl = upload_params.copy()
                upload_params_with_acl['ACL'] = 'public-read'
                self.client.put_object(**upload_params_with_acl)
                logger.info(f"Successfully uploaded file to S3 with public-read ACL: {file_key}")
            except ClientError as e:
                # If ACL fails, try without it
                if 'AccessControlListNotSupported' in str(e) or 'AccessDenied' in str(e):
                    logger.warning(f"Public ACL not supported, uploading without ACL: {file_key}")
                    self.client.put_object(**upload_params)
                    logger.info(f"Successfully uploaded file to S3 without ACL: {file_key}")
                else:
                    raise
            
            # Generate and return public URL
            s3_url = self._get_public_url(file_key)
            
            logger.info(f"Successfully uploaded file to S3: {file_key}")
            return s3_url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"S3 upload failed: {error_code} - {error_message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise
    
    def _generate_unique_key(self, file_type: str) -> str:
        """
        Generate a unique S3 key using UUID.
        
        Args:
            file_type: Type of file to determine folder structure
        
        Returns:
            str: Unique S3 key in format: {file_type}/{uuid}.jpg
        """
        unique_id = str(uuid.uuid4())
        # Organize files by type in S3
        return f"{file_type}/{unique_id}.jpg"
    
    def _get_public_url(self, file_key: str) -> str:
        """
        Generate public URL for an S3 object.
        
        Args:
            file_key: S3 object key
        
        Returns:
            str: Public HTTPS URL
        """
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}"
    
    def generate_presigned_url(
        self,
        file_key: str,
        expiration: int = 3600,
        http_method: str = 'PUT'
    ) -> str:
        """
        Generate a presigned URL for secure direct uploads from frontend.
        
        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds (default: 1 hour)
            http_method: HTTP method for the presigned URL (default: 'PUT')
        
        Returns:
            str: Presigned URL for direct upload
        
        Raises:
            ClientError: If presigned URL generation fails
        """
        try:
            presigned_url = self.client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key,
                    'ContentType': 'image/jpeg'
                },
                ExpiresIn=expiration,
                HttpMethod=http_method
            )
            
            logger.info(f"Generated presigned URL for key: {file_key}")
            return presigned_url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise
    
    def configure_bucket_cors(self, allowed_origins: list = None) -> None:
        """
        Configure CORS settings for the S3 bucket to allow frontend access.
        
        Args:
            allowed_origins: List of allowed origins (defaults to env var CORS_ORIGINS)
        
        Raises:
            ClientError: If CORS configuration fails
        """
        if allowed_origins is None:
            # Get from environment variable
            cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000')
            allowed_origins = [origin.strip() for origin in cors_origins.split(',')]
        
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': allowed_origins,
                    'ExposeHeaders': ['ETag'],
                    'MaxAgeSeconds': 3600
                }
            ]
        }
        
        try:
            self.client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration=cors_configuration
            )
            logger.info(f"Successfully configured CORS for bucket: {self.bucket_name}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Failed to configure CORS: {error_code} - {error_message}")
            raise
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete a file from S3.
        
        Args:
            file_key: S3 object key to delete
        
        Returns:
            bool: True if deletion was successful
        
        Raises:
            ClientError: If deletion fails
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"Successfully deleted file from S3: {file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file: {str(e)}")
            raise
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            file_key: S3 object key to check
        
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
