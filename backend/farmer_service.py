"""
Farmer service for FARM2FORK Platform

This module provides CRUD operations for farmer management including
get_or_create_farmer and farmer lookup by phone.

Requirements: 2.1, 2.2
"""

from sqlalchemy.orm import Session
from typing import Optional
from models import Farmer
import logging

logger = logging.getLogger(__name__)


def get_or_create_farmer(
    db: Session,
    phone: str,
    name: Optional[str] = None,
    location: Optional[str] = None
) -> Farmer:
    """
    Get existing farmer by phone or create new farmer.
    
    This function implements the get-or-create pattern for farmer accounts.
    If a farmer with the given phone number exists, it returns that farmer.
    Otherwise, it creates a new farmer record.
    
    Args:
        db: Database session
        phone: Phone number (unique identifier)
        name: Farmer name (required for new farmers)
        location: Farmer location (optional)
    
    Returns:
        Farmer: Existing or newly created farmer object
    
    Raises:
        ValueError: If name is not provided for new farmer creation
    
    Requirements: 2.1, 2.2
    """
    # Try to find existing farmer
    farmer = get_farmer_by_phone(db, phone)
    
    if farmer:
        logger.info(f"Found existing farmer with phone: {phone}")
        return farmer
    
    # Create new farmer
    if not name:
        raise ValueError("Name is required to create a new farmer")
    
    logger.info(f"Creating new farmer with phone: {phone}")
    
    farmer = Farmer(
        phone=phone,
        name=name,
        location=location
    )
    
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    
    logger.info(f"Created new farmer with id: {farmer.id}")
    
    return farmer


def get_farmer_by_phone(db: Session, phone: str) -> Optional[Farmer]:
    """
    Lookup farmer by phone number.
    
    Searches for a farmer with the given phone number in the database.
    
    Args:
        db: Database session
        phone: Phone number to search for
    
    Returns:
        Optional[Farmer]: Farmer object if found, None otherwise
    
    Requirements: 2.1, 2.2
    """
    if not phone:
        logger.warning("Empty phone number provided for lookup")
        return None
    
    farmer = db.query(Farmer).filter(Farmer.phone == phone).first()
    
    if farmer:
        logger.debug(f"Farmer found for phone: {phone}")
    else:
        logger.debug(f"No farmer found for phone: {phone}")
    
    return farmer


def get_farmer_by_id(db: Session, farmer_id: str) -> Optional[Farmer]:
    """
    Lookup farmer by ID.
    
    Searches for a farmer with the given UUID in the database.
    
    Args:
        db: Database session
        farmer_id: Farmer UUID to search for
    
    Returns:
        Optional[Farmer]: Farmer object if found, None otherwise
    
    Requirements: 2.1, 2.2
    """
    if not farmer_id:
        logger.warning("Empty farmer_id provided for lookup")
        return None
    
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    
    if farmer:
        logger.debug(f"Farmer found for id: {farmer_id}")
    else:
        logger.debug(f"No farmer found for id: {farmer_id}")
    
    return farmer


def update_farmer(
    db: Session,
    farmer_id: str,
    name: Optional[str] = None,
    location: Optional[str] = None
) -> Optional[Farmer]:
    """
    Update farmer information.
    
    Updates the name and/or location of an existing farmer.
    Only provided fields are updated.
    
    Args:
        db: Database session
        farmer_id: Farmer UUID
        name: New name (optional)
        location: New location (optional)
    
    Returns:
        Optional[Farmer]: Updated farmer object if found, None otherwise
    
    Requirements: 2.1, 2.2
    """
    farmer = get_farmer_by_id(db, farmer_id)
    
    if not farmer:
        logger.warning(f"Cannot update: farmer not found with id: {farmer_id}")
        return None
    
    # Update fields if provided
    if name is not None:
        farmer.name = name
        logger.debug(f"Updated farmer name to: {name}")
    
    if location is not None:
        farmer.location = location
        logger.debug(f"Updated farmer location to: {location}")
    
    db.commit()
    db.refresh(farmer)
    
    logger.info(f"Updated farmer with id: {farmer_id}")
    
    return farmer
