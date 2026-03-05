"""
Translate Service for FARM2FORK Platform

This module provides AWS Translate integration for multi-language support across
10 Indian languages. Implements translate_text and translate_batch methods for
translating UI content and AI-generated text.

Requirements: 4.6, 8.3, 8.5
"""

import boto3
import os
import copy
from typing import Dict, List, Optional
from botocore.exceptions import ClientError
from botocore.config import Config
import logging

logger = logging.getLogger(__name__)


class TranslateService:
    """Service class for AWS Translate operations"""
    
    def __init__(
        self,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize Translate service with AWS credentials.
        
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
        
        # Initialize Translate client
        self.client = boto3.client(
            'translate',
            region_name=self.region,
            aws_access_key_id=aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=config
        )
        
        # Language code mapping for 10 Indian languages
        self.language_map = {
            'en': 'en',  # English
            'hi': 'hi',  # Hindi
            'ta': 'ta',  # Tamil
            'te': 'te',  # Telugu
            'kn': 'kn',  # Kannada
            'ml': 'ml',  # Malayalam
            'bn': 'bn',  # Bengali
            'mr': 'mr',  # Marathi
            'gu': 'gu',  # Gujarati
            'pa': 'pa'   # Punjabi
        }
        
        logger.info(f"TranslateService initialized for region: {self.region}")
        logger.info(f"Supported languages: {', '.join(self.language_map.keys())}")
    
    def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        """
        Translate text between supported languages.
        
        This method translates a single text string from source language to
        target language using Amazon Translate. If source and target languages
        are the same, returns the original text without making an API call.
        
        Args:
            text: The text to translate
            source_language: Source language code (e.g., 'en', 'hi')
            target_language: Target language code (e.g., 'en', 'hi')
        
        Returns:
            str: Translated text in target language
        
        Raises:
            ValueError: If language codes are not supported
            ClientError: If AWS Translate API call fails
        
        Requirements: 4.6, 8.3, 8.5
        """
        # Validate language codes
        if source_language not in self.language_map:
            raise ValueError(
                f"Unsupported source language: {source_language}. "
                f"Supported languages: {', '.join(self.language_map.keys())}"
            )
        
        if target_language not in self.language_map:
            raise ValueError(
                f"Unsupported target language: {target_language}. "
                f"Supported languages: {', '.join(self.language_map.keys())}"
            )
        
        # Skip translation if source and target are the same
        if source_language == target_language:
            logger.debug(f"Source and target languages are the same ({source_language}), skipping translation")
            return text
        
        # Handle empty text
        if not text or not text.strip():
            logger.warning("Empty text provided for translation")
            return text
        
        try:
            logger.info(f"Translating text from {source_language} to {target_language}, length: {len(text)}")
            
            # Call AWS Translate
            response = self.client.translate_text(
                Text=text,
                SourceLanguageCode=self.language_map[source_language],
                TargetLanguageCode=self.language_map[target_language]
            )
            
            translated_text = response['TranslatedText']
            
            logger.info(f"Translation successful, output length: {len(translated_text)}")
            
            return translated_text
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS Translate error: {error_code} - {error_message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during translation: {str(e)}")
            raise
    
    def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str
    ) -> List[str]:
        """
        Translate multiple texts efficiently.
        
        This method translates a list of text strings from source language to
        target language. It processes each text individually but provides a
        convenient batch interface.
        
        Args:
            texts: List of text strings to translate
            source_language: Source language code (e.g., 'en', 'hi')
            target_language: Target language code (e.g., 'en', 'hi')
        
        Returns:
            List[str]: List of translated texts in the same order as input
        
        Raises:
            ValueError: If language codes are not supported
            ClientError: If AWS Translate API call fails
        
        Requirements: 4.6, 8.3, 8.5
        """
        # Skip translation if source and target are the same
        if source_language == target_language:
            logger.debug(f"Source and target languages are the same ({source_language}), skipping batch translation")
            return texts
        
        # Validate language codes (will raise ValueError if invalid)
        if source_language not in self.language_map:
            raise ValueError(
                f"Unsupported source language: {source_language}. "
                f"Supported languages: {', '.join(self.language_map.keys())}"
            )
        
        if target_language not in self.language_map:
            raise ValueError(
                f"Unsupported target language: {target_language}. "
                f"Supported languages: {', '.join(self.language_map.keys())}"
            )
        
        logger.info(f"Translating batch of {len(texts)} texts from {source_language} to {target_language}")
        
        translated = []
        for i, text in enumerate(texts):
            try:
                translated_text = self.translate_text(text, source_language, target_language)
                translated.append(translated_text)
                logger.debug(f"Translated text {i+1}/{len(texts)}")
            except Exception as e:
                logger.error(f"Failed to translate text {i+1}/{len(texts)}: {str(e)}")
                # Re-raise to fail fast on any error
                raise
        
        logger.info(f"Batch translation complete: {len(translated)} texts translated")
        
        return translated
    
    def translate_verification_data(
        self,
        verification_data: Dict,
        target_language: str
    ) -> Dict:
        """
        Translate all user-facing text in verification response.
        
        This method translates safety explanations and consumption advice
        while preserving data values (dates, numbers, names). Only UI labels
        and AI-generated text are translated.
        
        Args:
            verification_data: Dictionary containing verification data with structure:
                {
                    'safety_analysis': {
                        'explanation': str,
                        ...
                    },
                    'consumption_advice': {
                        'how_to_clean': str,
                        'safety_tips': str,
                        'consumption_recommendations': str
                    }
                }
            target_language: Target language code (e.g., 'en', 'hi')
        
        Returns:
            Dict: Verification data with translated text fields
        
        Requirements: 8.5, 8.6, 8.8
        """
        # Skip translation if target is English (default language)
        if target_language == 'en':
            logger.debug("Target language is English, skipping translation")
            return verification_data
        
        # Validate target language
        if target_language not in self.language_map:
            raise ValueError(
                f"Unsupported target language: {target_language}. "
                f"Supported languages: {', '.join(self.language_map.keys())}"
            )
        
        logger.info(f"Translating verification data to {target_language}")
        
        # Create a deep copy to avoid modifying the original
        translated_data = copy.deepcopy(verification_data)
        
        # Translate safety explanation if present
        if 'safety_analysis' in translated_data and translated_data['safety_analysis']:
            if 'explanation' in translated_data['safety_analysis']:
                explanation = translated_data['safety_analysis']['explanation']
                if explanation and explanation.strip():
                    try:
                        translated_explanation = self.translate_text(
                            explanation,
                            'en',
                            target_language
                        )
                        translated_data['safety_analysis']['explanation'] = translated_explanation
                        logger.debug("Translated safety explanation")
                    except Exception as e:
                        logger.error(f"Failed to translate safety explanation: {str(e)}")
                        # Keep original text on error
        
        # Translate consumption advice if present
        if 'consumption_advice' in translated_data and translated_data['consumption_advice']:
            advice_fields = ['how_to_clean', 'safety_tips', 'consumption_recommendations']
            
            for field in advice_fields:
                if field in translated_data['consumption_advice']:
                    text = translated_data['consumption_advice'][field]
                    if text and text.strip():
                        try:
                            translated_text = self.translate_text(
                                text,
                                'en',
                                target_language
                            )
                            translated_data['consumption_advice'][field] = translated_text
                            logger.debug(f"Translated consumption advice field: {field}")
                        except Exception as e:
                            logger.error(f"Failed to translate {field}: {str(e)}")
                            # Keep original text on error
        
        logger.info(f"Verification data translation complete for language: {target_language}")
        
        return translated_data
