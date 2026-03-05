# Alembic Database Migrations

This directory contains Alembic database migrations for the FARM2FORK platform.

## Overview

Alembic is used to manage database schema changes in a version-controlled manner. Each migration represents a change to the database schema and can be applied or rolled back.

## Migration Files

### Initial Migration (8f7130b062dd)
Creates all base tables for the platform:
- `farmers` - Farmer account information
- `crop_batches` - Crop batch metadata
- `crop_images` - Crop images with Rekognition analysis
- `treatments` - Pesticide and fertilizer applications
- `safety_analyses` - AI-generated safety scores
- `qr_codes` - QR codes for consumer verification

### Performance Indexes (af53e32d9465)
Adds indexes for frequently queried columns:
- `idx_crop_batches_farmer` - Index on crop_batches.farmer_id
- `idx_crop_images_batch` - Index on crop_images.batch_id
- `idx_treatments_batch` - Index on treatments.batch_id
- `idx_safety_analyses_batch` - Index on safety_analyses.batch_id
- `idx_qr_codes_qr_id` - Index on qr_codes.qr_id (most critical for consumer queries)

## Usage

### Prerequisites

Ensure you have:
1. PostgreSQL database running
2. DATABASE_URL environment variable set
3. Alembic installed (`pip install alembic`)

### Apply Migrations

To upgrade to the latest version:
```bash
cd backend
alembic upgrade head
```

To upgrade to a specific revision:
```bash
alembic upgrade <revision_id>
```

### Rollback Migrations

To downgrade one version:
```bash
alembic downgrade -1
```

To downgrade to a specific revision:
```bash
alembic downgrade <revision_id>
```

To rollback all migrations:
```bash
alembic downgrade base
```

### Check Current Version

To see the current database version:
```bash
alembic current
```

### View Migration History

To see all migrations:
```bash
alembic history
```

To see verbose history with details:
```bash
alembic history --verbose
```

## Creating New Migrations

### Auto-generate Migration (requires database connection)

When you modify models in `models.py`, generate a migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Manual Migration

To create an empty migration file:
```bash
alembic revision -m "Description of changes"
```

Then edit the generated file in `alembic/versions/` to add your changes.

## Configuration

### Database URL

The database URL is configured via the `DATABASE_URL` environment variable. The default is:
```
postgresql://username:password@localhost:5432/farm2fork
```

For production, set this to your AWS RDS PostgreSQL connection string:
```
postgresql://user:password@your-rds-endpoint.region.rds.amazonaws.com:5432/farm2fork
```

### Environment Variables

Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/farm2fork
```

## Production Deployment

For AWS Lambda deployment:

1. **Before deployment**: Run migrations locally or from a bastion host that can access RDS
2. **Set DATABASE_URL**: Configure the RDS connection string in Lambda environment variables
3. **Run migrations**: Execute `alembic upgrade head` before deploying the Lambda function

### Migration Script for CI/CD

```bash
#!/bin/bash
# migrate.sh - Run database migrations

set -e

echo "Running database migrations..."
cd backend
alembic upgrade head
echo "Migrations completed successfully!"
```

## Troubleshooting

### Connection Refused Error

If you get a connection error:
1. Ensure PostgreSQL is running
2. Check DATABASE_URL is correct
3. Verify database credentials
4. Check firewall/security group settings (for RDS)

### Migration Conflicts

If you have migration conflicts:
1. Check `alembic history` to see the current state
2. Use `alembic downgrade` to rollback if needed
3. Resolve conflicts in migration files
4. Re-run `alembic upgrade head`

### Offline Mode

To generate SQL without executing (useful for review):
```bash
alembic upgrade head --sql > migration.sql
```

## Best Practices

1. **Always review auto-generated migrations** - Alembic may not catch all changes correctly
2. **Test migrations on a copy of production data** before applying to production
3. **Keep migrations small and focused** - One logical change per migration
4. **Never modify existing migrations** that have been applied to production
5. **Always provide both upgrade() and downgrade()** functions
6. **Document complex migrations** with comments in the migration file

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
