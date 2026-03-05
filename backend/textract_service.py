"""
Textract Service for FARM2FORK Platform

This module provides Amazon Textract integration for OCR text extraction from
seed packets, pesticide packages, and fertilizer packages. Implements extract_from_image
method using analyze_document API, parses response to extract raw text and key-value pairs,
and calculates confidence scores.

Requirements: 3.2, 3.3, 3.4
"""

import boto3
import os
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError
from botocore.config import Config
import logging

logger = logging.getLogger(__name__)


class TextractService:
    """Service class for AWS Textract OCR operations"""
    
    def __init__(
        self,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize Textract service with AWS credentials.
        
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
        
        # Initialize Textract client
        self.client = boto3.client(
            'textract',
            region_name=self.region,
            aws_access_key_id=aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=config
        )
        
        logger.info(f"TextractService initialized for region: {self.region}")
    
    def extract_from_image(self, s3_bucket: str, s3_key: str) -> Dict[str, Any]:
        """
        Extract text and key-value pairs from document image using Textract analyze_document API.
        
        Args:
            s3_bucket: S3 bucket name containing the image
            s3_key: S3 object key of the image
        
        Returns:
            Dict containing:
                - raw_text: Extracted text content as a single string
                - key_value_pairs: Dictionary of detected key-value pairs
                - confidence: Average confidence score (0-100)
        
        Raises:
            ClientError: If Textract API call fails
        """
        try:
            # Call Textract analyze_document with FORMS and TABLES features
            response = self.client.analyze_document(
                Document={
                    'S3Object': {
                        'Bucket': s3_bucket,
                        'Name': s3_key
                    }
                },
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            # Parse response to extract structured data
            extracted_data = {
                'raw_text': self._extract_text(response),
                'key_value_pairs': self._extract_key_values(response),
                'confidence': self._calculate_confidence(response)
            }
            
            logger.info(f"Successfully extracted text from {s3_key} with confidence {extracted_data['confidence']:.2f}%")
            return extracted_data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Textract extraction failed: {error_code} - {error_message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Textract extraction: {str(e)}")
            raise
    
    def _extract_text(self, response: Dict) -> str:
        """
        Extract all text content from Textract response.
        
        Args:
            response: Textract analyze_document response
        
        Returns:
            str: Concatenated text from all LINE blocks
        """
        text_lines = []
        
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text_lines.append(block.get('Text', ''))
        
        return '\n'.join(text_lines)
    
    def _extract_key_values(self, response: Dict) -> Dict[str, str]:
        """
        Extract key-value pairs from Textract FORMS analysis.
        
        Args:
            response: Textract analyze_document response
        
        Returns:
            Dict: Key-value pairs detected in the document
        """
        # Build a map of block IDs to blocks for quick lookup
        block_map = {block['Id']: block for block in response.get('Blocks', [])}
        
        key_value_pairs = {}
        
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block.get('EntityTypes', []):
                    # This is a key block
                    key_text = self._get_text_from_relationship(block, block_map)
                    
                    # Find the associated value
                    value_text = ''
                    if 'Relationships' in block:
                        for relationship in block['Relationships']:
                            if relationship['Type'] == 'VALUE':
                                # Get the value block
                                for value_id in relationship['Ids']:
                                    value_block = block_map.get(value_id)
                                    if value_block:
                                        value_text = self._get_text_from_relationship(value_block, block_map)
                    
                    if key_text:
                        key_value_pairs[key_text] = value_text
        
        return key_value_pairs
    
    def _get_text_from_relationship(self, block: Dict, block_map: Dict) -> str:
        """
        Extract text from a block's child relationships.
        
        Args:
            block: Textract block with relationships
            block_map: Map of block IDs to blocks
        
        Returns:
            str: Concatenated text from child blocks
        """
        text_parts = []
        
        if 'Relationships' in block:
            for relationship in block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        child_block = block_map.get(child_id)
                        if child_block and child_block['BlockType'] == 'WORD':
                            text_parts.append(child_block.get('Text', ''))
        
        return ' '.join(text_parts)
    
    def _calculate_confidence(self, response: Dict) -> float:
        """
        Calculate average confidence score from all detected blocks.
        
        Args:
            response: Textract analyze_document response
        
        Returns:
            float: Average confidence score (0-100)
        """
        confidences = []
        
        for block in response.get('Blocks', []):
            if 'Confidence' in block:
                confidences.append(block['Confidence'])
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)
    
    def extract_seed_packet_info(self, extracted_data: Dict) -> Dict[str, Optional[str]]:
        """
        Parse seed packet specific information from extracted data.
        Uses pattern matching to identify crop name, variety, and planting details.
        
        Args:
            extracted_data: Dictionary containing raw_text and key_value_pairs from extract_from_image
        
        Returns:
            Dict containing:
                - crop_name: Name of the crop
                - crop_variety: Variety or type of the crop
                - planting_season: Recommended planting season
        
        Requirements: 3.2
        """
        result = {
            'crop_name': None,
            'crop_variety': None,
            'planting_season': None
        }
        
        raw_text = extracted_data.get('raw_text', '').lower()
        key_value_pairs = extracted_data.get('key_value_pairs', {})
        
        # Search in key-value pairs first (more structured)
        for key, value in key_value_pairs.items():
            key_lower = key.lower()
            
            # Look for crop name
            if any(term in key_lower for term in ['crop', 'name', 'product', 'seed']):
                if value and not result['crop_name']:
                    result['crop_name'] = value.strip()
            
            # Look for variety
            if any(term in key_lower for term in ['variety', 'type', 'cultivar', 'hybrid']):
                if value and not result['crop_variety']:
                    result['crop_variety'] = value.strip()
            
            # Look for planting season
            if any(term in key_lower for term in ['season', 'planting', 'sowing', 'time']):
                if value and not result['planting_season']:
                    result['planting_season'] = value.strip()
        
        # Fallback: pattern matching in raw text if key-value pairs didn't yield results
        if not result['crop_name']:
            result['crop_name'] = self._find_field_in_text(
                raw_text, 
                ['crop:', 'name:', 'product:', 'seed:']
            )
        
        if not result['crop_variety']:
            result['crop_variety'] = self._find_field_in_text(
                raw_text,
                ['variety:', 'type:', 'cultivar:', 'hybrid:']
            )
        
        if not result['planting_season']:
            result['planting_season'] = self._find_field_in_text(
                raw_text,
                ['season:', 'planting:', 'sowing:', 'best time:']
            )
        
        logger.info(f"Extracted seed packet info: {result}")
        return result
    
    def extract_pesticide_info(self, extracted_data: Dict) -> Dict[str, Optional[str]]:
        """
        Parse pesticide package information from extracted data.
        Uses pattern matching to identify pesticide name, active ingredient, and dosage.
        
        Args:
            extracted_data: Dictionary containing raw_text and key_value_pairs from extract_from_image
        
        Returns:
            Dict containing:
                - name: Name of the pesticide product
                - active_ingredient: Active chemical ingredient
                - dosage: Recommended dosage or application rate
        
        Requirements: 3.3
        """
        result = {
            'name': None,
            'active_ingredient': None,
            'dosage': None
        }
        
        raw_text = extracted_data.get('raw_text', '')
        raw_text_lower = raw_text.lower()
        key_value_pairs = extracted_data.get('key_value_pairs', {})
        
        # Search in key-value pairs first
        for key, value in key_value_pairs.items():
            key_lower = key.lower()
            
            # Look for product name
            if any(term in key_lower for term in ['product', 'name', 'pesticide', 'brand']):
                if value and not result['name']:
                    result['name'] = value.strip()
            
            # Look for active ingredient
            if any(term in key_lower for term in ['active', 'ingredient', 'composition', 'chemical']):
                if value and not result['active_ingredient']:
                    result['active_ingredient'] = value.strip()
            
            # Look for dosage
            if any(term in key_lower for term in ['dosage', 'dose', 'application rate', 'rate', 'quantity', 'usage']):
                if value and not result['dosage']:
                    result['dosage'] = value.strip()
        
        # Fallback: pattern matching in raw text
        if not result['name']:
            result['name'] = self._find_field_in_text(
                raw_text_lower,
                ['product:', 'name:', 'pesticide:', 'brand:']
            )
        
        # If still no name, use the first line (common for pesticide packages)
        if not result['name']:
            lines = raw_text.strip().split('\n')
            if lines:
                first_line = lines[0].strip()
                # Only use if it's not too long and doesn't contain common non-name words
                if first_line and len(first_line) < 50 and not any(word in first_line.lower() for word in ['controls', 'usage', 'dosage', 'application']):
                    result['name'] = first_line
        
        if not result['active_ingredient']:
            result['active_ingredient'] = self._find_field_in_text(
                raw_text_lower,
                ['active ingredient:', 'ingredient:', 'composition:', 'chemical:']
            )
        
        if not result['dosage']:
            # Look for dosage patterns in text
            dosage = self._find_field_in_text(
                raw_text_lower,
                ['dosage:', 'dose:', 'application rate:', 'rate:', 'recommended:', 'usage:']
            )
            
            # If not found, look for common dosage patterns (e.g., "2-2.5 g per litre")
            if not dosage:
                import re
                # Pattern for dosage like "2-2.5 g per litre" or "10ml per liter"
                dosage_pattern = r'(\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\s*(g|ml|kg|l|grams?|milliliters?|liters?|litres?)\s*(?:per|/)\s*(litre|liter|kg|hectare|acre)'
                match = re.search(dosage_pattern, raw_text_lower)
                if match:
                    dosage = match.group(0)
            
            result['dosage'] = dosage
        
        logger.info(f"Extracted pesticide info: {result}")
        return result
    
    def extract_fertilizer_info(self, extracted_data: Dict) -> Dict[str, Optional[str]]:
        """
        Parse fertilizer package information from extracted data.
        Uses pattern matching to identify fertilizer name, NPK ratio, and quantity.
        
        Args:
            extracted_data: Dictionary containing raw_text and key_value_pairs from extract_from_image
        
        Returns:
            Dict containing:
                - name: Name of the fertilizer product
                - npk_ratio: NPK composition ratio (e.g., "10-20-10")
                - quantity: Package quantity or weight
        
        Requirements: 3.4
        """
        result = {
            'name': None,
            'npk_ratio': None,
            'quantity': None
        }
        
        raw_text = extracted_data.get('raw_text', '').lower()
        key_value_pairs = extracted_data.get('key_value_pairs', {})
        
        # Search in key-value pairs first
        for key, value in key_value_pairs.items():
            key_lower = key.lower()
            
            # Look for product name
            if any(term in key_lower for term in ['product', 'name', 'fertilizer', 'brand']):
                if value and not result['name']:
                    result['name'] = value.strip()
            
            # Look for NPK ratio
            if any(term in key_lower for term in ['npk', 'ratio', 'composition', 'grade', 'formula']):
                if value and not result['npk_ratio']:
                    result['npk_ratio'] = value.strip()
            
            # Look for quantity
            if any(term in key_lower for term in ['quantity', 'weight', 'volume', 'net', 'content']):
                if value and not result['quantity']:
                    result['quantity'] = value.strip()
        
        # Fallback: pattern matching in raw text
        if not result['name']:
            result['name'] = self._find_field_in_text(
                raw_text,
                ['product:', 'name:', 'fertilizer:', 'brand:']
            )
        
        if not result['npk_ratio']:
            result['npk_ratio'] = self._find_field_in_text(
                raw_text,
                ['npk:', 'ratio:', 'composition:', 'grade:', 'formula:']
            )
        
        if not result['quantity']:
            result['quantity'] = self._find_field_in_text(
                raw_text,
                ['quantity:', 'weight:', 'volume:', 'net weight:', 'net content:']
            )
        
        logger.info(f"Extracted fertilizer info: {result}")
        return result
    
    def _find_field_in_text(self, text: str, patterns: List[str]) -> Optional[str]:
        """
        Find a field value in raw text using pattern matching.
        
        Args:
            text: Raw text to search (should be lowercase)
            patterns: List of patterns to search for (e.g., ['crop:', 'name:'])
        
        Returns:
            str: Extracted value after the pattern with proper capitalization, or None if not found
        """
        for pattern in patterns:
            if pattern in text:
                # Find the position after the pattern
                start_idx = text.index(pattern) + len(pattern)
                
                # Extract text until newline or end of string
                remaining_text = text[start_idx:].strip()
                
                # Take the first line or first few words
                value = remaining_text.split('\n')[0].strip()
                
                # Limit to reasonable length (first 100 chars)
                if len(value) > 100:
                    value = value[:100].strip()
                
                if value:
                    # Capitalize the first letter of each word for proper formatting
                    return value.title()
        
        return None
