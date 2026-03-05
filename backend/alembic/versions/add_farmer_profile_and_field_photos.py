"""add farmer profile and field photos

Revision ID: add_farmer_photos
Revises: af53e32d9465
Create Date: 2026-03-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_farmer_photos'
down_revision = 'af53e32d9465'
branch_labels = None
depends_on = None


def upgrade():
    # Add profile_photo_url to farmers table
    op.add_column('farmers', sa.Column('profile_photo_url', sa.Text(), nullable=True))
    
    # Add field_photo_url to crop_batches table
    op.add_column('crop_batches', sa.Column('field_photo_url', sa.Text(), nullable=True))


def downgrade():
    # Remove the columns
    op.drop_column('crop_batches', 'field_photo_url')
    op.drop_column('farmers', 'profile_photo_url')
