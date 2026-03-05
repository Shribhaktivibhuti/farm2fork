"""
Authentication utilities for FARM2FORK Platform

This module provides JWT token generation/validation, password hashing,
and OTP validation for farmer authentication.

Requirements: 2.1, 2.2
"""

import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Demo OTP for testing
DEMO_OTP = "0000"


def validate_otp(otp: str) -> bool:
    """
    Validate OTP for farmer authentication.
    
    In demo mode, accepts "0000" as valid OTP.
    In production, this would integrate with SMS OTP service.
    
    Args:
        otp: The OTP string to validate
    
    Returns:
        bool: True if OTP is valid, False otherwise
    
    Requirements: 2.1, 2.2
    """
    if not otp:
        logger.warning("Empty OTP provided")
        return False
    
    # Demo mode: accept "0000"
    if otp == DEMO_OTP:
        logger.info("Demo OTP validated successfully")
        return True
    
    # In production, implement actual OTP validation logic here
    # For now, only demo OTP is accepted
    logger.warning(f"Invalid OTP provided: {otp}")
    return False


def generate_jwt_token(farmer_id: str, phone: str) -> str:
    """
    Generate JWT token for authenticated farmer.
    
    Creates a JWT token containing farmer ID and phone number
    with expiration time.
    
    Args:
        farmer_id: UUID of the farmer
        phone: Phone number of the farmer
    
    Returns:
        str: JWT token string
    
    Requirements: 2.1, 2.2
    """
    # Calculate expiration time
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    # Create payload
    payload = {
        "farmer_id": str(farmer_id),
        "phone": phone,
        "exp": expiration,
        "iat": datetime.utcnow()
    }
    
    # Generate token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    logger.info(f"JWT token generated for farmer_id: {farmer_id}")
    
    return token


def validate_jwt_token(token: str) -> Optional[Dict]:
    """
    Validate JWT token and extract payload.
    
    Verifies the token signature and expiration, then returns
    the decoded payload.
    
    Args:
        token: JWT token string
    
    Returns:
        Optional[Dict]: Decoded payload if valid, None if invalid
    
    Requirements: 2.1, 2.2
    """
    try:
        # Decode and validate token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        logger.info(f"JWT token validated for farmer_id: {payload.get('farmer_id')}")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating JWT token: {str(e)}")
        return None


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    This function is for future use when password-based authentication
    is implemented. Currently, the system uses OTP-only authentication.
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    hashed = pwd_context.hash(password)
    logger.debug("Password hashed successfully")
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    This function is for future use when password-based authentication
    is implemented. Currently, the system uses OTP-only authentication.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
    
    Returns:
        bool: True if password matches, False otherwise
    """
    is_valid = pwd_context.verify(plain_password, hashed_password)
    logger.debug(f"Password verification result: {is_valid}")
    return is_valid


def extract_token_from_header(authorization_header: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    
    Expects header format: "Bearer <token>"
    
    Args:
        authorization_header: Authorization header value
    
    Returns:
        Optional[str]: Token string if valid format, None otherwise
    """
    if not authorization_header:
        logger.warning("Empty authorization header")
        return None
    
    parts = authorization_header.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Invalid authorization header format: {authorization_header}")
        return None
    
    return parts[1]
