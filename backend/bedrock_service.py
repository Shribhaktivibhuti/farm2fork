"""
Bedrock Service for FARM2FORK Platform

This module provides AWS Bedrock integration for AI-powered safety analysis and
consumption recommendations. Implements invoke_model wrapper with error handling,
supports both Claude and Amazon Nova models for generating safety scores and consumption advice.

Requirements: 4.1, 4.2, 4.3, 4.4
"""

import boto3
import json
import os
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from botocore.config import Config
import logging

logger = logging.getLogger(__name__)


class BedrockService:
    """Service class for AWS Bedrock AI operations"""
    
    def __init__(
        self,
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize Bedrock service with AWS credentials.
        
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
        
        # Initialize Bedrock runtime client
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=self.region,
            aws_access_key_id=aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=config
        )
        
        # Set model ID to Claude 3 Haiku (fast and cost-effective)
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
        
        logger.info(f"BedrockService initialized for region: {self.region}, model: {self.model_id}")
    
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Invoke Bedrock model with error handling.
        
        This is a wrapper method that handles the Bedrock API call with proper
        error handling and retry logic. Supports both Claude and Amazon Nova models.
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in the response (default: 1000)
            temperature: Model temperature for response variability (default: 0.7)
        
        Returns:
            str: The model's text response
        
        Raises:
            ClientError: If Bedrock API call fails
            ValueError: If response parsing fails
        """
        try:
            # Determine model type and prepare appropriate request body
            if 'anthropic.claude' in self.model_id:
                # Claude API format
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            elif 'amazon.nova' in self.model_id:
                # Amazon Nova API format
                request_body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature
                    }
                }
            else:
                # Default to Nova format for other Amazon models
                request_body = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt}]
                        }
                    ],
                    "inferenceConfig": {
                        "max_new_tokens": max_tokens,
                        "temperature": temperature
                    }
                }
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text based on model type
            if 'anthropic.claude' in self.model_id:
                # Claude response format
                if 'content' in response_body and len(response_body['content']) > 0:
                    text_response = response_body['content'][0]['text']
                    logger.info(f"Successfully invoked Bedrock model, response length: {len(text_response)}")
                    return text_response
            else:
                # Nova response format
                if 'output' in response_body and 'message' in response_body['output']:
                    content = response_body['output']['message']['content']
                    if content and len(content) > 0:
                        text_response = content[0]['text']
                        logger.info(f"Successfully invoked Bedrock model, response length: {len(text_response)}")
                        return text_response
            
            raise ValueError("Invalid response format from Bedrock model")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"Bedrock invocation failed: {error_code} - {error_message}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bedrock response: {str(e)}")
            raise ValueError(f"Invalid JSON in Bedrock response: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during Bedrock invocation: {str(e)}")
            raise
    
    def _format_treatments(self, treatments: list) -> str:
        """
        Format treatment list for prompt inclusion.
        
        Args:
            treatments: List of treatment dictionaries
        
        Returns:
            str: Formatted treatment information
        """
        if not treatments:
            return "None"
        
        formatted = []
        for treatment in treatments:
            name = treatment.get('name', 'Unknown')
            dosage = treatment.get('dosage_or_quantity', 'Not specified')
            app_date = treatment.get('application_date', 'Unknown')
            formatted.append(f"  - {name} (Dosage: {dosage}, Applied: {app_date})")
        
        return "\n".join(formatted)
    
    def _build_safety_prompt(
        self,
        crop_name: str,
        farming_method: str,
        pesticides: list,
        fertilizers: list,
        harvest_date: str,
        rekognition_data: Optional[Dict] = None
    ) -> str:
        """
        Build comprehensive prompt for safety analysis.
        
        Args:
            crop_name: Name of the crop
            farming_method: Farming method (organic/conventional/integrated)
            pesticides: List of pesticide treatment dictionaries
            fertilizers: List of fertilizer treatment dictionaries
            harvest_date: Harvest date string
            rekognition_data: Optional Rekognition analysis results
        
        Returns:
            str: Formatted prompt for Bedrock
        """
        rekognition_section = ""
        if rekognition_data:
            rekognition_section = f"\nImage Analysis Results:\n{json.dumps(rekognition_data, indent=2)}\n"
        
        prompt = f"""You are a food safety expert analyzing agricultural produce for consumer safety.

Crop Information:
- Crop: {crop_name}
- Farming Method: {farming_method}
- Harvest Date: {harvest_date}

Pesticides Used:
{self._format_treatments(pesticides)}

Fertilizers Used:
{self._format_treatments(fertilizers)}
{rekognition_section}
Please provide a comprehensive safety analysis with:
1. Safety Score (0-100): A numerical score where 100 is completely safe
2. Risk Level: Classify as "Safe" (71-100), "Moderate" (41-70), or "Risk" (0-40)
3. Explanation: A clear, consumer-friendly explanation of the safety assessment

Consider:
- Time elapsed since pesticide application (minimum safe intervals)
- Type and toxicity of pesticides used
- Farming method and its impact on safety
- Visual quality indicators from image analysis (if available)
- Standard food safety guidelines

Format your response as JSON:
{{
  "safety_score": <number>,
  "risk_level": "<Safe|Moderate|Risk>",
  "explanation": "<detailed explanation>"
}}"""
        
        return prompt
    
    def _parse_safety_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse safety analysis response from Bedrock.
        
        Args:
            response_text: Raw text response from Bedrock
        
        Returns:
            Dict containing safety_score, risk_level, and explanation
        
        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        try:
            # Try to extract JSON from response
            # Sometimes the model includes text before/after JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.error(f"No JSON found in response: {response_text[:200]}")
                raise ValueError("No JSON object found in response")
            
            json_str = response_text[start_idx:end_idx]
            
            # Try parsing without cleaning first
            try:
                analysis = json.loads(json_str)
            except json.JSONDecodeError:
                # If that fails, try cleaning control characters
                json_str_cleaned = json_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                analysis = json.loads(json_str_cleaned)
            
            # Validate required fields
            if 'safety_score' not in analysis:
                raise ValueError("Missing 'safety_score' in response")
            if 'risk_level' not in analysis:
                raise ValueError("Missing 'risk_level' in response")
            if 'explanation' not in analysis:
                raise ValueError("Missing 'explanation' in response")
            
            # Validate safety_score range (0-100)
            score = float(analysis['safety_score'])
            if not (0 <= score <= 100):
                raise ValueError(f"Safety score {score} is out of valid range (0-100)")
            
            # Validate risk_level enum
            risk_level = analysis['risk_level']
            valid_risk_levels = ['Safe', 'Moderate', 'Risk']
            if risk_level not in valid_risk_levels:
                raise ValueError(f"Invalid risk_level '{risk_level}'. Must be one of {valid_risk_levels}")
            
            # Validate explanation is non-empty
            if not analysis['explanation'] or not analysis['explanation'].strip():
                raise ValueError("Explanation cannot be empty")
            
            logger.info(f"Successfully parsed safety analysis: score={score}, risk={risk_level}")
            
            return {
                'safety_score': score,
                'risk_level': risk_level,
                'explanation': analysis['explanation']
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from safety response: {str(e)}")
            raise ValueError(f"Invalid JSON in safety analysis response: {str(e)}")
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid response structure: {str(e)}")
            raise ValueError(f"Invalid response structure: {str(e)}")
    
    def generate_safety_analysis(
        self,
        crop_name: str,
        farming_method: str,
        pesticides: list,
        fertilizers: list,
        harvest_date: str,
        rekognition_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive safety analysis using Bedrock.
        
        This method builds a comprehensive prompt with crop data, treatments,
        and Rekognition results, invokes the Bedrock model, and parses the
        JSON response to extract safety_score, risk_level, and explanation.
        
        Args:
            crop_name: Name of the crop
            farming_method: Farming method (organic/conventional/integrated)
            pesticides: List of pesticide treatment dictionaries with keys:
                       name, dosage_or_quantity, application_date
            fertilizers: List of fertilizer treatment dictionaries with keys:
                        name, dosage_or_quantity, application_date
            harvest_date: Harvest date as string
            rekognition_data: Optional dict with Rekognition analysis results
        
        Returns:
            Dict containing:
                - safety_score (float): Score from 0-100
                - risk_level (str): 'Safe', 'Moderate', or 'Risk'
                - explanation (str): Consumer-friendly safety explanation
        
        Raises:
            ClientError: If Bedrock API call fails
            ValueError: If response parsing or validation fails
        
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        logger.info(f"Generating safety analysis for crop: {crop_name}")
        
        # Build comprehensive prompt
        prompt = self._build_safety_prompt(
            crop_name=crop_name,
            farming_method=farming_method,
            pesticides=pesticides,
            fertilizers=fertilizers,
            harvest_date=harvest_date,
            rekognition_data=rekognition_data
        )
        
        # Invoke Bedrock model
        response_text = self.invoke_model(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse and validate response
        analysis = self._parse_safety_response(response_text)
        
        logger.info(f"Safety analysis complete: {analysis['risk_level']} (score: {analysis['safety_score']})")
        
        return analysis
    
    def _build_consumption_advice_prompt(
        self,
        crop_name: str,
        safety_analysis: Dict[str, Any],
        treatments: Dict[str, list],
        language: str = 'en'
    ) -> str:
        """
        Build prompt for consumption advice generation.
        
        Args:
            crop_name: Name of the crop
            safety_analysis: Dict with safety_score, risk_level, explanation
            treatments: Dict with 'pesticides' and 'fertilizers' lists
            language: Target language code (default: 'en')
        
        Returns:
            str: Formatted prompt for Bedrock
        """
        language_names = {
            'en': 'English',
            'hi': 'Hindi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'bn': 'Bengali',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'pa': 'Punjabi'
        }
        
        language_name = language_names.get(language, 'English')
        
        prompt = f"""You are a food safety advisor helping consumers understand how to safely consume produce.

Crop: {crop_name}
Safety Score: {safety_analysis.get('safety_score', 'N/A')}
Risk Level: {safety_analysis.get('risk_level', 'N/A')}

Treatments Applied:
Pesticides:
{self._format_treatments(treatments.get('pesticides', []))}

Fertilizers:
{self._format_treatments(treatments.get('fertilizers', []))}

Please provide practical advice in {language_name} language on:
1. How to clean and prepare this produce to remove pesticide residues
2. Safety tips for consumption
3. Recommendations on who should or shouldn't consume this (children, pregnant women, etc.)

Format as JSON:
{{
  "how_to_clean": "<step-by-step cleaning instructions>",
  "safety_tips": "<important safety considerations>",
  "consumption_recommendations": "<who can consume, serving suggestions>"
}}"""
        
        return prompt
    
    def _parse_consumption_advice_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse consumption advice response from Bedrock.
        
        Args:
            response_text: Raw text response from Bedrock
        
        Returns:
            Dict containing how_to_clean, safety_tips, consumption_recommendations
        
        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON object found in response")
            
            json_str = response_text[start_idx:end_idx]
            
            # Clean up control characters that might break JSON parsing
            json_str = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            
            advice = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['how_to_clean', 'safety_tips', 'consumption_recommendations']
            for field in required_fields:
                if field not in advice:
                    raise ValueError(f"Missing '{field}' in response")
                if not advice[field] or not advice[field].strip():
                    raise ValueError(f"Field '{field}' cannot be empty")
            
            logger.info("Successfully parsed consumption advice")
            
            return {
                'how_to_clean': advice['how_to_clean'],
                'safety_tips': advice['safety_tips'],
                'consumption_recommendations': advice['consumption_recommendations']
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from consumption advice response: {str(e)}")
            raise ValueError(f"Invalid JSON in consumption advice response: {str(e)}")
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid response structure: {str(e)}")
            raise ValueError(f"Invalid response structure: {str(e)}")
    
    def generate_consumption_advice(
        self,
        crop_name: str,
        safety_analysis: Dict[str, Any],
        treatments: Dict[str, list],
        language: str = 'en'
    ) -> Dict[str, str]:
        """
        Generate personalized consumption advice using Bedrock.
        
        This method builds a prompt for cleaning instructions, safety tips,
        and consumption recommendations, supports language parameter for
        multilingual advice, and parses the JSON response.
        
        Args:
            crop_name: Name of the crop
            safety_analysis: Dict containing safety_score, risk_level, explanation
            treatments: Dict with 'pesticides' and 'fertilizers' lists
            language: Target language code (default: 'en')
                     Supported: en, hi, ta, te, kn, ml, bn, mr, gu, pa
        
        Returns:
            Dict containing:
                - how_to_clean (str): Step-by-step cleaning instructions
                - safety_tips (str): Important safety considerations
                - consumption_recommendations (str): Who can consume, serving suggestions
        
        Raises:
            ClientError: If Bedrock API call fails
            ValueError: If response parsing or validation fails
        
        Requirements: 7.8, 7.9, 7.10, 7.11
        """
        logger.info(f"Generating consumption advice for crop: {crop_name}, language: {language}")
        
        # Build consumption advice prompt
        prompt = self._build_consumption_advice_prompt(
            crop_name=crop_name,
            safety_analysis=safety_analysis,
            treatments=treatments,
            language=language
        )
        
        # Invoke Bedrock model
        response_text = self.invoke_model(
            prompt=prompt,
            max_tokens=800,
            temperature=0.7
        )
        
        # Parse and validate response
        advice = self._parse_consumption_advice_response(response_text)
        
        logger.info(f"Consumption advice generated successfully for language: {language}")
        
        return advice
