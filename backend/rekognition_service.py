"""
Rekognition Service for FARM2FORK Platform

This module provides AWS Rekognition integration for analyzing crop images.
Implements analyze_crop_image using detect_labels API with MinConfidence set to 70%,
parses labels and categories from response, and extracts crop quality indicators.

Requirements: 4.5
"""

import boto3
import os
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError
from botocore.config import Config
import logging

logger = logging.getLogger(__name__)


class RekognitionService:
    """Service class for AWS Rekognition operations"""
    
    def __init__(
        self,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize Rekognition service with AWS credentials.
        
        Args:
            region: AWS region (defaults to env var AWS_REGION)
            aws_access_key_id: AWS access key (defaults to env var)
            aws_secret_access_key: AWS secret key (defaults to env var)
        """
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        
        # Configure boto3 client with retry logic
        config = Config(
            region_name=self.region,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            }
        )
        
        # Initialize Rekognition client
        self.client = boto3.client(
            'rekognition',
            region_name=self.region,
            aws_access_key_id=aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=config
        )
        
        logger.info(f"RekognitionService initialized for region: {self.region}")
    
    def analyze_crop_image(self, s3_bucket: str, s3_key: str) -> Dict[str, Any]:
        """
        Detect labels and quality indicators in crop images using Rekognition.
        
        This method uses the detect_labels API with MinConfidence set to 70%
        to analyze crop images and extract visual characteristics and quality indicators.
        
        Args:
            s3_bucket: S3 bucket name where the image is stored
            s3_key: S3 object key of the image
        
        Returns:
            Dict containing:
                - labels: List of detected labels with name, confidence, and categories
                - crop_indicators: Quality indicators (freshness, ripeness, damage, disease)
        
        Raises:
            ClientError: If Rekognition API call fails
        
        Requirements: 4.5
        """
        try:
            # Detect labels with MinConfidence set to 70%
            response = self.client.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': s3_bucket,
                        'Name': s3_key
                    }
                },
                MaxLabels=20,
                MinConfidence=70.0
            )
            
            # Parse labels and categories from response
            labels = self._parse_labels(response)
            
            # Extract crop quality indicators
            crop_indicators = self._extract_crop_indicators(response)
            
            logger.info(f"Successfully analyzed crop image: {s3_key}, found {len(labels)} labels")
            
            return {
                'labels': labels,
                'crop_indicators': crop_indicators
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Rekognition analysis failed: {error_code} - {error_message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Rekognition analysis: {str(e)}")
            raise
    
    def _parse_labels(self, response: Dict) -> List[Dict[str, Any]]:
        """
        Parse labels and categories from Rekognition response.
        
        Args:
            response: Raw Rekognition detect_labels response
        
        Returns:
            List of parsed labels with name, confidence, and categories
        """
        labels = []
        
        for label in response.get('Labels', []):
            parsed_label = {
                'name': label['Name'],
                'confidence': label['Confidence'],
                'categories': []
            }
            
            # Extract categories if present
            if 'Categories' in label:
                parsed_label['categories'] = [
                    category['Name'] for category in label['Categories']
                ]
            
            labels.append(parsed_label)
        
        return labels
    
    def _extract_crop_indicators(self, response: Dict) -> Dict[str, float]:
        """
        Extract crop-specific quality indicators from detected labels.
        
        Maps detected labels to quality indicators:
        - freshness: Indicators of fresh, green, healthy produce
        - ripeness: Indicators of ripe, mature produce
        - damage: Indicators of damaged, bruised, wilted produce
        - disease: Indicators of disease, pest, infection
        
        Args:
            response: Raw Rekognition detect_labels response
        
        Returns:
            Dict with quality indicator scores (0-100)
        """
        indicators = {
            'freshness': 0.0,
            'ripeness': 0.0,
            'damage': 0.0,
            'disease': 0.0
        }
        
        # Define keyword mappings for quality indicators
        freshness_keywords = ['fresh', 'green', 'healthy', 'vibrant', 'crisp']
        ripeness_keywords = ['ripe', 'mature', 'ready']
        damage_keywords = ['damaged', 'bruised', 'wilted', 'brown', 'spotted', 'blemish']
        disease_keywords = ['disease', 'pest', 'infection', 'mold', 'rot', 'fungus']
        
        # Map labels to quality indicators
        for label in response.get('Labels', []):
            name = label['Name'].lower()
            confidence = label['Confidence']
            
            # Check for freshness indicators
            if any(keyword in name for keyword in freshness_keywords):
                indicators['freshness'] = max(indicators['freshness'], confidence)
            
            # Check for ripeness indicators
            if any(keyword in name for keyword in ripeness_keywords):
                indicators['ripeness'] = max(indicators['ripeness'], confidence)
            
            # Check for damage indicators
            if any(keyword in name for keyword in damage_keywords):
                indicators['damage'] = max(indicators['damage'], confidence)
            
            # Check for disease indicators
            if any(keyword in name for keyword in disease_keywords):
                indicators['disease'] = max(indicators['disease'], confidence)
        
        return indicators
