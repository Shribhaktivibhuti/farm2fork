"""Initial migration - create all tables

Revision ID: 8f7130b062dd
Revises: 
Create Date: 2026-02-28 15:39:50.505456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8f7130b062dd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for FARM2FORK platform."""
    
    # Create farmers table
    op.create_table(
        'farmers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('phone', sa.String(15), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create index on phone for faster lookups
    op.create_index('ix_farmers_phone', 'farmers', ['phone'])
    
    # Create crop_batches table
    op.create_table(
        'crop_batches',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('farmer_id', sa.String(36), nullable=False),
        sa.Column('crop_name', sa.String(255), nullable=False),
        sa.Column('crop_variety', sa.String(255), nullable=True),
        sa.Column('farming_method', sa.String(50), nullable=False),
        sa.Column('harvest_date', sa.Date(), nullable=False),
        sa.Column('seed_packet_image_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ondelete='CASCADE'),
    )
    
    # Create crop_images table
    op.create_table(
        'crop_images',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('batch_id', sa.String(36), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('rekognition_labels', sa.JSON(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['batch_id'], ['crop_batches.id'], ondelete='CASCADE'),
    )
    
    # Create treatments table
    op.create_table(
        'treatments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('batch_id', sa.String(36), nullable=False),
        sa.Column('treatment_type', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('dosage_or_quantity', sa.String(100), nullable=True),
        sa.Column('application_date', sa.Date(), nullable=False),
        sa.Column('package_image_url', sa.Text(), nullable=True),
        sa.Column('extracted_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['batch_id'], ['crop_batches.id'], ondelete='CASCADE'),
    )
    
    # Create safety_analyses table
    op.create_table(
        'safety_analyses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('batch_id', sa.String(36), nullable=False, unique=True),
        sa.Column('safety_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('risk_level', sa.String(20), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('bedrock_model', sa.String(100), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['batch_id'], ['crop_batches.id'], ondelete='CASCADE'),
    )
    
    # Create qr_codes table
    op.create_table(
        'qr_codes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('qr_id', sa.String(50), nullable=False, unique=True),
        sa.Column('batch_id', sa.String(36), nullable=False, unique=True),
        sa.Column('qr_code_url', sa.Text(), nullable=False),
        sa.Column('scan_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['batch_id'], ['crop_batches.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('qr_codes')
    op.drop_table('safety_analyses')
    op.drop_table('treatments')
    op.drop_table('crop_images')
    op.drop_table('crop_batches')
    op.drop_index('ix_farmers_phone', 'farmers')
    op.drop_table('farmers')
