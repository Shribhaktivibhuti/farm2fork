"""
Database configuration for FARM2FORK Platform.
Supports both PostgreSQL (production) and SQLite (development).
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./farm2fork.db')

# SQLite specific configuration
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {"check_same_thread": False}

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database by creating all tables"""
    Base.metadata.create_all(bind=engine)
