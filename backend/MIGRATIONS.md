# Database Migrations Guide

This guide explains how to manage database migrations for the FARM2FORK platform using Alembic.

## Quick Start

### 1. Set Up Database Connection

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` and set your PostgreSQL connection details:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/farm2fork
```

### 2. Run Migrations

Apply all migrations to create the database schema:

```bash
cd backend
python migrate.py upgrade
```

Or use Alembic directly:

```bash
alembic upgrade head
```

### 3. Verify Migration Status

Check the current database version:

```bash
python migrate.py current
```

## Migration Files

The platform includes two migrations:

### Migration 1: Initial Tables (8f7130b062dd)

Creates all base tables:
- **farmers** - Farmer accounts with phone authentication
- **crop_batches** - Crop batch metadata (crop name, variety, farming method, harvest date)
- **crop_images** - Crop images with Amazon Rekognition analysis results
- **treatments** - Pesticide and fertilizer application records
- **safety_analyses** - AI-generated safety scores from Amazon Bedrock
- **qr_codes** - QR codes for consumer verification

### Migration 2: Performance Indexes (af53e32d9465)

Adds indexes for optimized query performance:
- `idx_crop_batches_farmer` - Fast farmer batch lookups
- `idx_crop_images_batch` - Fast batch image retrieval
- `idx_treatments_batch` - Fast treatment history queries
- `idx_safety_analyses_batch` - Fast safety analysis lookups
- `idx_qr_codes_qr_id` - **Critical** for consumer QR code scanning

## Common Commands

### Apply Migrations

```bash
# Apply all pending migrations
python migrate.py upgrade

# Or with Alembic
alembic upgrade head
```

### Rollback Migrations

```bash
# Rollback one migration
python migrate.py downgrade

# Or with Alembic
alembic downgrade -1

# Rollback to a specific version
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Check Status

```bash
# Show current version
python migrate.py current

# Show migration history
python migrate.py history

# Or with Alembic
alembic current
alembic history --verbose
```

### Generate SQL (without executing)

```bash
# Generate SQL for review
alembic upgrade head --sql > migration.sql
```

## Creating New Migrations

### Auto-generate from Model Changes

When you modify `models.py`, generate a migration:

```bash
alembic revision --autogenerate -m "Add new column to farmers table"
```

**Important**: Always review auto-generated migrations before applying!

### Manual Migration

Create an empty migration file:

```bash
alembic revision -m "Add custom index"
```

Then edit the file in `alembic/versions/` to add your changes.

## Production Deployment

### AWS RDS PostgreSQL

1. **Set DATABASE_URL** to your RDS endpoint:
   ```env
   DATABASE_URL=postgresql://user:pass@your-rds.region.rds.amazonaws.com:5432/farm2fork
   ```

2. **Run migrations** from a machine that can access RDS:
   ```bash
   python migrate.py upgrade
   ```

3. **Verify** the migration succeeded:
   ```bash
   python migrate.py current
   ```

### CI/CD Pipeline

Add migration step to your deployment pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run Database Migrations
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    cd backend
    pip install -r requirements.txt
    python migrate.py upgrade
```

## Troubleshooting

### Connection Refused

**Problem**: Cannot connect to PostgreSQL

**Solutions**:
1. Ensure PostgreSQL is running: `pg_ctl status`
2. Check DATABASE_URL is correct
3. Verify credentials: `psql -U username -d farm2fork`
4. For RDS: Check security group allows your IP

### Migration Already Applied

**Problem**: "Target database is not up to date"

**Solution**: Check current version and history:
```bash
alembic current
alembic history
```

### Rollback Failed

**Problem**: Cannot rollback migration

**Solution**: Check the downgrade() function in the migration file is correct

### Offline Mode

If you need to generate migrations without a database connection, use offline mode by modifying `alembic/env.py` to skip the database connection check.

## Database Schema

### Entity Relationships

```
Farmer (1) ──< (N) CropBatch
                    │
                    ├──< (N) CropImage
                    ├──< (N) Treatment
                    ├──< (1) SafetyAnalysis
                    └──< (1) QRCode
```

### Key Constraints

- **Unique Constraints**: 
  - `farmers.phone` - One account per phone number
  - `qr_codes.qr_id` - Unique QR identifiers
  - `safety_analyses.batch_id` - One analysis per batch
  - `qr_codes.batch_id` - One QR code per batch

- **Foreign Keys**: All child tables cascade delete when parent is deleted

- **Indexes**: Optimized for common queries (farmer batches, QR lookups)

## Best Practices

1. ✅ **Always backup production data** before running migrations
2. ✅ **Test migrations on staging** before production
3. ✅ **Review auto-generated migrations** - they may miss some changes
4. ✅ **Keep migrations small** - one logical change per migration
5. ✅ **Never modify applied migrations** - create a new migration instead
6. ✅ **Document complex migrations** with comments
7. ✅ **Provide both upgrade and downgrade** functions

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [AWS RDS PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)

## Support

For issues or questions:
1. Check `alembic/README.md` for detailed Alembic documentation
2. Review migration files in `alembic/versions/`
3. Check application logs for error details
4. Verify DATABASE_URL environment variable is set correctly
