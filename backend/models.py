"""
Database models for FARM2FORK AI-Powered Traceability Platform.

This module defines all SQLAlchemy ORM models for the platform:
- Farmer: Farmer account information
- CropBatch: Crop batch metadata and farming details
- CropImage: Images of crops with Rekognition analysis results
- Treatment: Pesticide and fertilizer application records
- SafetyAnalysis: AI-generated safety scores and risk assessments
- QRCode: QR codes linking to crop batch verification data

All models use UUID primary keys and include proper relationships,
indexes, and cascade delete behavior.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric, Date, Text, Index
from sqlalchemy.orm import relationship
from database import Base


class Farmer(Base):
    """Farmer account model"""
    __tablename__ = 'farmers'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(15), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    profile_photo_url = Column(Text)  # Farmer profile photo
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    batches = relationship("CropBatch", back_populates="farmer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Farmer(id={self.id}, name={self.name}, phone={self.phone})>"


class CropBatch(Base):
    """Crop batch model"""
    __tablename__ = 'crop_batches'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farmer_id = Column(String(36), ForeignKey('farmers.id'), nullable=False)
    crop_name = Column(String(255), nullable=False)
    crop_variety = Column(String(255))
    farming_method = Column(String(50), nullable=False)
    harvest_date = Column(Date, nullable=False)
    seed_packet_image_url = Column(Text)
    field_photo_url = Column(Text)  # Photo of the farmer's field
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    farmer = relationship("Farmer", back_populates="batches")
    images = relationship("CropImage", back_populates="batch", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="batch", cascade="all, delete-orphan")
    safety_analysis = relationship("SafetyAnalysis", back_populates="batch", uselist=False, cascade="all, delete-orphan")
    qr_code = relationship("QRCode", back_populates="batch", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CropBatch(id={self.id}, crop_name={self.crop_name}, farmer_id={self.farmer_id})>"


Index('idx_crop_batches_farmer', CropBatch.farmer_id)


class CropImage(Base):
    """Crop image model"""
    __tablename__ = 'crop_images'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey('crop_batches.id', ondelete='CASCADE'), nullable=False)
    image_url = Column(Text, nullable=False)
    rekognition_labels = Column(Text)  # JSON as text for SQLite
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    batch = relationship("CropBatch", back_populates="images")
    
    def __repr__(self):
        return f"<CropImage(id={self.id}, batch_id={self.batch_id})>"


Index('idx_crop_images_batch', CropImage.batch_id)


class Treatment(Base):
    """Treatment model"""
    __tablename__ = 'treatments'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey('crop_batches.id', ondelete='CASCADE'), nullable=False)
    treatment_type = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    dosage_or_quantity = Column(String(100))
    application_date = Column(Date, nullable=False)
    package_image_url = Column(Text)
    extracted_data = Column(Text)  # JSON as text for SQLite
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    batch = relationship("CropBatch", back_populates="treatments")
    
    def __repr__(self):
        return f"<Treatment(id={self.id}, type={self.treatment_type}, name={self.name})>"


Index('idx_treatments_batch', Treatment.batch_id)


class SafetyAnalysis(Base):
    """Safety analysis model"""
    __tablename__ = 'safety_analyses'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey('crop_batches.id', ondelete='CASCADE'), nullable=False, unique=True)
    safety_score = Column(Numeric(5, 2), nullable=False)
    risk_level = Column(String(20), nullable=False)
    explanation = Column(Text, nullable=False)
    bedrock_model = Column(String(100))
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    batch = relationship("CropBatch", back_populates="safety_analysis")
    
    def __repr__(self):
        return f"<SafetyAnalysis(id={self.id}, batch_id={self.batch_id}, score={self.safety_score})>"


Index('idx_safety_analyses_batch', SafetyAnalysis.batch_id)


class QRCode(Base):
    """QR code model"""
    __tablename__ = 'qr_codes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qr_id = Column(String(50), unique=True, nullable=False)
    batch_id = Column(String(36), ForeignKey('crop_batches.id', ondelete='CASCADE'), nullable=False, unique=True)
    qr_code_url = Column(Text, nullable=False)
    scan_count = Column(Integer, default=0, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    batch = relationship("CropBatch", back_populates="qr_code")
    
    def __repr__(self):
        return f"<QRCode(id={self.id}, qr_id={self.qr_id}, batch_id={self.batch_id})>"


Index('idx_qr_codes_qr_id', QRCode.qr_id)
