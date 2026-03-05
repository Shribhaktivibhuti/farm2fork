# Database Configuration - PostgreSQL RDS

## Current Setup

**Database**: PostgreSQL on AWS RDS  
**Host**: farm2fork-db.c1mkkqcsufe9.eu-north-1.rds.amazonaws.com  
**Port**: 5432  
**Database**: farm2fork-db  
**User**: farmadmin  
**Password**: farmadmin  

## Status

✅ Backend started successfully  
✅ Connected to PostgreSQL RDS  
⚠️ Connection might be slow (network latency to eu-north-1)  

## Configuration Applied

Updated `backend/.env`:
```
DATABASE_URL=postgresql://farmadmin:farmadmin@farm2fork-db.c1mkkqcsufe9.eu-north-1.rds.amazonaws.com:5432/farm2fork-db
DB_HOST=farm2fork-db.c1mkkqcsufe9.eu-north-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=farm2fork-db
DB_USER=farmadmin
DB_PASSWORD=farmadmin
```

## Testing

### Test Login Now:
1. Go to: **http://localhost:5175/farmer/login**
2. Phone: **9999999999**
3. OTP: **0000**
4. Name: **Your Name**
5. Location: **Your City**
6. Click **Login**

### If Login is Slow:
- This is normal - the database is in EU (eu-north-1)
- First request might take 5-10 seconds
- Subsequent requests will be faster

### If Login Fails:
Check backend logs for errors:
- Database connection timeout
- Table doesn't exist
- Network issues

## Database Tables

The database should have these tables:
- farmers
- crop_batches
- crop_images
- treatments
- safety_analyses
- qr_codes

If tables don't exist, they might need to be created via Alembic migrations.

## Services Running

- **Backend**: http://localhost:8000 (PostgreSQL)
- **Frontend**: http://localhost:5175
- **Database**: PostgreSQL RDS (eu-north-1)

## Next Steps

1. **Test login** from the frontend
2. If it works: Create a batch and test full flow
3. If it's too slow: Consider switching to local PostgreSQL or SQLite
4. If tables are missing: Run Alembic migrations

## Troubleshooting

### Slow Performance
- Database is in Europe (eu-north-1), you might be far away
- Consider using a closer region or local database

### Connection Timeout
- Check if RDS security group allows your IP
- Check if RDS is publicly accessible
- Verify credentials are correct

### Tables Don't Exist
Run Alembic migrations:
```bash
cd backend
alembic upgrade head
```

## Alternative: Use Local Database

If RDS is too slow or inaccessible, switch back to SQLite:
```
DATABASE_URL=sqlite:///./farm2fork.db
```

Then restart backend and run:
```bash
python backend/init_db.py
```
