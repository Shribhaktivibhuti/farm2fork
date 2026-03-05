"""Add performance indexes

Revision ID: af53e32d9465
Revises: 8f7130b062dd
Create Date: 2026-02-28 15:47:45.317731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af53e32d9465'
down_revision: Union[str, None] = '8f7130b062dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for frequently queried columns."""
    
    # Index for crop_batches.farmer_id - used when fetching farmer's batches
    op.create_index('idx_crop_batches_farmer', 'crop_batches', ['farmer_id'])
    
    # Index for crop_images.batch_id - used when fetching batch images
    op.create_index('idx_crop_images_batch', 'crop_images', ['batch_id'])
    
    # Index for treatments.batch_id - used when fetching batch treatments
    op.create_index('idx_treatments_batch', 'treatments', ['batch_id'])
    
    # Index for safety_analyses.batch_id - used when fetching batch safety analysis
    op.create_index('idx_safety_analyses_batch', 'safety_analyses', ['batch_id'])
    
    # Index for qr_codes.qr_id - most common query for consumer verification
    op.create_index('idx_qr_codes_qr_id', 'qr_codes', ['qr_id'])


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('idx_qr_codes_qr_id', 'qr_codes')
    op.drop_index('idx_safety_analyses_batch', 'safety_analyses')
    op.drop_index('idx_treatments_batch', 'treatments')
    op.drop_index('idx_crop_images_batch', 'crop_images')
    op.drop_index('idx_crop_batches_farmer', 'crop_batches')
