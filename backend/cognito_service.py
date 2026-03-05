"""
AWS Cognito Service for FARM2FORK Platform

This module provides AWS Cognito integration for SMS OTP authentication.
Implements phone number-based authentication with SMS OTP verification.

Production-ready implementation with proper error handling and security.
"""

import boto3
import os
import hmac
import hashlib
import base64
import requests
from typing import Dict, Optional, Tuple
from botocore.exceptions import ClientError
from jose import jwt, JWTError
from jose.backends import RSAKey
import logging
import json

logger = logging.getLogger(__name__)


class CognitoService:
    """Service class for AWS Cognito authentication operations"""
    
    def __init__(
        self,
        user_pool_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        region: Optional[str] = None
    ):
        """
        Initialize Cognito service with AWS credentials.
        
        Args:
            user_pool_id: Cognito User Pool ID
            client_id: Cognito App Client ID
            client_secret: Cognito App Client Secret
            region: AWS region
        """
        self.user_pool_id = user_pool_id or os.getenv('COGNITO_USER_POOL_ID')
        self.client_id = client_id or os.getenv('COGNITO_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('COGNITO_CLIENT_SECRET')
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        
        # Validate required configuration
        if not all([self.user_pool_id, self.client_id, self.region]):
            raise ValueError("Missing required Cognito configuration")
        
        # Initialize Cognito client
        self.client = boto3.client(
            'cognito-idp',
            region_name=self.region,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # JWKS URL for token validation
        self.jwks_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        self._jwks_cache = None
        
        logger.info(f"CognitoService initialized for pool: {self.user_pool_id}")
    
    def _calculate_secret_hash(self, username: str) -> str:
        """
        Calculate SECRET_HASH for Cognito authentication.
        
        Required when app client has a secret configured.
        
        Args:
            username: Username (phone number)
        
        Returns:
            str: Base64 encoded secret hash
        """
        if not self.client_secret:
            return None
        
        message = bytes(username + self.client_id, 'utf-8')
        secret = bytes(self.client_secret, 'utf-8')
        dig = hmac.new(secret, message, hashlib.sha256).digest()
        return base64.b64encode(dig).decode()
    
    def initiate_auth(self, phone_number: str) -> Dict:
        """
        Initiate authentication flow and send SMS OTP.
        
        Creates or retrieves user and triggers SMS OTP delivery.
        
        Args:
            phone_number: Phone number in E.164 format (e.g., +919876543210)
        
        Returns:
            Dict containing:
                - success: bool
                - session: str (session token for OTP verification)
                - message: str
        
        Raises:
            ClientError: If Cognito API call fails
        """
        try:
            # Normalize phone number to E.164 format
            if not phone_number.startswith('+'):
                # Assume Indian number if no country code
                phone_number = f"+91{phone_number.lstrip('0')}"
            
            logger.info(f"Initiating auth for phone: {phone_number}")
            
            # Calculate secret hash if client secret exists
            secret_hash = self._calculate_secret_hash(phone_number)
            
            # Prepare auth parameters
            auth_params = {
                'USERNAME': phone_number,
                'AUTH_FLOW': 'CUSTOM_AUTH'
            }
            
            if secret_hash:
                auth_params['SECRET_HASH'] = secret_hash
            
            # Initiate authentication
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='CUSTOM_AUTH',
                AuthParameters=auth_params
            )
            
            logger.info(f"OTP sent successfully to {phone_number}")
            
            return {
                'success': True,
                'session': response.get('Session'),
                'message': 'OTP sent successfully'
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"Cognito initiate_auth failed: {error_code} - {error_message}")
            
            # Handle specific errors
            if error_code == 'UserNotFoundException':
                # Auto-create user if not exists
                return self._create_user_and_send_otp(phone_number)
            elif error_code == 'TooManyRequestsException':
                return {
                    'success': False,
                    'error': 'too_many_requests',
                    'message': 'Too many attempts. Please try again later.'
                }
            else:
                return {
                    'success': False,
                    'error': error_code,
                    'message': error_message
                }
        
        except Exception as e:
            logger.error(f"Unexpected error in initiate_auth: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Authentication service error'
            }
    
    def _create_user_and_send_otp(self, phone_number: str) -> Dict:
        """
        Create new user in Cognito and send OTP.
        
        Args:
            phone_number: Phone number in E.164 format
        
        Returns:
            Dict with success status and session
        """
        try:
            logger.info(f"Creating new user: {phone_number}")
            
            # Create user with phone number as username
            self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=phone_number,
                UserAttributes=[
                    {'Name': 'phone_number', 'Value': phone_number},
                    {'Name': 'phone_number_verified', 'Value': 'true'}
                ],
                MessageAction='SUPPRESS'  # Don't send welcome email
            )
            
            # Now initiate auth to send OTP
            return self.initiate_auth(phone_number)
            
        except ClientError as e:
            logger.error(f"Failed to create user: {str(e)}")
            return {
                'success': False,
                'error': 'user_creation_failed',
                'message': 'Failed to create user account'
            }
    
    def verify_otp(self, phone_number: str, otp: str, session: Optional[str] = None) -> Dict:
        """
        Verify OTP and complete authentication.
        
        Args:
            phone_number: Phone number in E.164 format
            otp: OTP code received via SMS
            session: Session token from initiate_auth (optional)
        
        Returns:
            Dict containing:
                - success: bool
                - id_token: str (Cognito ID token)
                - access_token: str (Cognito access token)
                - refresh_token: str (Cognito refresh token)
                - user_attributes: dict
        
        Raises:
            ClientError: If verification fails
        """
        try:
            # Normalize phone number
            if not phone_number.startswith('+'):
                phone_number = f"+91{phone_number.lstrip('0')}"
            
            logger.info(f"Verifying OTP for phone: {phone_number}")
            
            # Calculate secret hash
            secret_hash = self._calculate_secret_hash(phone_number)
            
            # Prepare challenge responses
            challenge_responses = {
                'USERNAME': phone_number,
                'ANSWER': otp
            }
            
            if secret_hash:
                challenge_responses['SECRET_HASH'] = secret_hash
            
            # Respond to auth challenge
            response = self.client.respond_to_auth_challenge(
                ClientId=self.client_id,
                ChallengeName='CUSTOM_CHALLENGE',
                Session=session,
                ChallengeResponses=challenge_responses
            )
            
            # Extract tokens
            auth_result = response.get('AuthenticationResult', {})
            
            if not auth_result:
                logger.warning(f"OTP verification failed for {phone_number}")
                return {
                    'success': False,
                    'error': 'invalid_otp',
                    'message': 'Invalid or expired OTP'
                }
            
            # Get user attributes
            user_attributes = self._get_user_attributes(auth_result['AccessToken'])
            
            logger.info(f"OTP verified successfully for {phone_number}")
            
            return {
                'success': True,
                'id_token': auth_result.get('IdToken'),
                'access_token': auth_result.get('AccessToken'),
                'refresh_token': auth_result.get('RefreshToken'),
                'expires_in': auth_result.get('ExpiresIn', 3600),
                'user_attributes': user_attributes
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"OTP verification failed: {error_code} - {error_message}")
            
            # Handle specific errors
            if error_code == 'NotAuthorizedException':
                return {
                    'success': False,
                    'error': 'invalid_otp',
                    'message': 'Incorrect OTP. Please try again.'
                }
            elif error_code == 'CodeMismatchException':
                return {
                    'success': False,
                    'error': 'invalid_otp',
                    'message': 'Incorrect OTP. Please try again.'
                }
            elif error_code == 'ExpiredCodeException':
                return {
                    'success': False,
                    'error': 'expired_otp',
                    'message': 'OTP has expired. Please request a new one.'
                }
            else:
                return {
                    'success': False,
                    'error': error_code,
                    'message': error_message
                }
        
        except Exception as e:
            logger.error(f"Unexpected error in verify_otp: {str(e)}")
            return {
                'success': False,
                'error': 'internal_error',
                'message': 'Verification service error'
            }
    
    def _get_user_attributes(self, access_token: str) -> Dict:
        """
        Get user attributes from Cognito.
        
        Args:
            access_token: Cognito access token
        
        Returns:
            Dict of user attributes
        """
        try:
            response = self.client.get_user(AccessToken=access_token)
            
            attributes = {}
            for attr in response.get('UserAttributes', []):
                attributes[attr['Name']] = attr['Value']
            
            return attributes
            
        except Exception as e:
            logger.error(f"Failed to get user attributes: {str(e)}")
            return {}
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate Cognito JWT token using JWKS.
        
        Verifies token signature, expiration, and issuer.
        
        Args:
            token: Cognito ID token or access token
        
        Returns:
            Optional[Dict]: Decoded token payload if valid, None if invalid
        """
        try:
            # Get JWKS keys
            if not self._jwks_cache:
                self._jwks_cache = self._fetch_jwks()
            
            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                logger.warning("Token missing 'kid' in header")
                return None
            
            # Find matching key
            key = None
            for jwk in self._jwks_cache.get('keys', []):
                if jwk.get('kid') == kid:
                    key = jwk
                    break
            
            if not key:
                logger.warning(f"No matching key found for kid: {kid}")
                return None
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=self.client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            logger.info(f"Token validated successfully for user: {payload.get('sub')}")
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error validating token: {str(e)}")
            return None
    
    def _fetch_jwks(self) -> Dict:
        """
        Fetch JWKS (JSON Web Key Set) from Cognito.
        
        Returns:
            Dict containing JWKS keys
        """
        try:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {str(e)}")
            return {'keys': []}
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Cognito refresh token
        
        Returns:
            Dict with new tokens
        """
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            auth_result = response.get('AuthenticationResult', {})
            
            return {
                'success': True,
                'id_token': auth_result.get('IdToken'),
                'access_token': auth_result.get('AccessToken'),
                'expires_in': auth_result.get('ExpiresIn', 3600)
            }
            
        except ClientError as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return {
                'success': False,
                'error': 'refresh_failed',
                'message': 'Failed to refresh token'
            }
