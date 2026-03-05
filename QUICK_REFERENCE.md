# FARM2FORK Quick Reference Card

## 🚀 Quick Start Commands

### Start Everything
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend  
cd frontend && npm run dev
```

### With Docker
```bash
docker-compose up
```

## 📍 URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5174 | React app |
| Backend | http://localhost:8000 | FastAPI API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | API documentation |

## 🔑 Demo Credentials

| Field | Value |
|-------|-------|
| Phone | Any 10-digit number |
| OTP | 0000 |

## 📡 API Endpoints

### Public (No Auth)
```
GET  /health
GET  /api/crops
GET  /api/languages
GET  /api/public/verify/{qr_id}
POST /api/public/translate
```

### Authenticated (Requires Bearer Token)
```
POST /api/auth/login
POST /api/batch/create
GET  /api/farmer/batches
POST /api/qr/generate
POST /api/upload/presigned-url
POST /api/extract/pesticide
POST /api/extract/fertilizer
POST /api/batch/analyze
```

## 🔐 Authentication

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"1234567890","otp":"0000"}'
```

### Use Token
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/farmer/batches
```

## 📦 Predefined Data

### Crops
- Tomato (Cherry, Beefsteak, Roma, Heirloom)
- Potato (Russet, Red, Yukon Gold, Fingerling)
- Onion (Red, White, Yellow, Sweet)
- Rice (Basmati, Jasmine, Arborio, Brown)
- Wheat (Hard Red, Soft White, Durum, Spelt)
- Carrot (Nantes, Imperator, Chantenay, Baby)

### Languages
- en (English)
- hi (Hindi)
- ta (Tamil)
- te (Telugu)
- kn (Kannada)
- ml (Malayalam)
- bn (Bengali)
- mr (Marathi)
- gu (Gujarati)
- pa (Punjabi)

## 🗄️ Database

### Check Data
```bash
cd backend
python -c "from database import SessionLocal; from models import *; db = SessionLocal(); print('Farmers:', db.query(Farmer).count()); print('Batches:', db.query(CropBatch).count())"
```

### Reset Database
```bash
cd backend
rm farm2fork.db
python init_db.py
```

## 🐳 Docker Commands

### Build
```bash
docker build -t farm2fork-backend backend/
```

### Run
```bash
docker run -p 8000:8000 --env-file backend/.env farm2fork-backend
```

### Compose
```bash
docker-compose up -d        # Start
docker-compose logs -f      # View logs
docker-compose down         # Stop
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov
```

### Manual API Test
```bash
# Health check
curl http://localhost:8000/health

# Get crops
curl http://localhost:8000/api/crops

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"1234567890","otp":"0000"}'
```

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Backend Won't Start
```bash
cd backend
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

### Frontend Won't Start
```bash
cd frontend
npm install
npm install html5-qrcode
npm run dev
```

### Database Issues
```bash
cd backend
rm farm2fork.db
python init_db.py
```

## 📊 Environment Variables

### Backend (.env)
```bash
DATABASE_URL=sqlite:///./farm2fork.db
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=farm2fork-images
JWT_SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:5174
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## 🚢 Deployment

### Backend to EC2
```bash
docker build -t farm2fork-backend .
docker push YOUR_ECR_REPO
ssh ec2-user@your-ec2-ip
docker pull YOUR_ECR_REPO
docker run -d -p 8000:8000 --env-file .env YOUR_ECR_REPO
```

### Frontend to S3
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://farm2fork-frontend --delete
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| START_HERE.md | Quick start guide |
| FINAL_SUMMARY.md | Complete overview |
| TEST_GUIDE.md | Testing instructions |
| DEPLOYMENT_GUIDE.md | Production deployment |
| ARCHITECTURE.md | System architecture |
| QUICK_REFERENCE.md | This file |

## 🎯 Common Tasks

### Create a Batch
1. Login at http://localhost:5174
2. Click "Farmer Mode"
3. Login with phone + OTP
4. Click "Create New Batch"
5. Fill form and submit

### Generate QR
1. Go to dashboard
2. Find your batch
3. Click "Generate QR"
4. View/download QR code

### Verify Product
1. Click "Consumer Mode"
2. Scan QR or enter ID
3. View verification

### Translate
1. On verification page
2. Select language
3. Click "Translate"

## 🔍 Useful Queries

### Get All Batches
```sql
SELECT * FROM crop_batches ORDER BY created_at DESC;
```

### Get Batch with QR
```sql
SELECT b.*, q.qr_id 
FROM crop_batches b 
LEFT JOIN qr_codes q ON b.id = q.batch_id;
```

### Get Farmer Stats
```sql
SELECT 
  f.name,
  COUNT(b.id) as batch_count,
  COUNT(q.id) as qr_count
FROM farmers f
LEFT JOIN crop_batches b ON f.id = b.farmer_id
LEFT JOIN qr_codes q ON b.id = q.batch_id
GROUP BY f.id;
```

## 🎨 UI Components

### Colors
- Farmer: Green (#16a34a)
- Consumer: Blue (#2563eb)
- Success: Green (#22c55e)
- Error: Red (#ef4444)
- Warning: Yellow (#eab308)

### Icons
- Farmer: 🚜
- Consumer: 🛒
- Batch: 📦
- QR: 📱
- Analysis: 🤖
- Verified: ✅

## 🔗 Important Links

- GitHub: [Your repo]
- API Docs: http://localhost:8000/docs
- Postman: postman/FARM2FORK.postman_collection.json
- AWS Console: https://console.aws.amazon.com

## 💡 Pro Tips

1. Use Swagger UI for API testing
2. Check browser console for errors
3. Use Postman collection for automation
4. Enable AWS CloudWatch for monitoring
5. Use docker-compose for local dev
6. Keep .env files secure
7. Test with real AWS credentials
8. Monitor API rate limits
9. Use CDN for production
10. Enable database backups

## 🆘 Get Help

1. Check documentation files
2. Review API docs at /docs
3. Check logs in console
4. Test with Postman
5. Verify environment variables
6. Check AWS service status
7. Review error messages
8. Test with curl commands

## ✅ Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables set
- [ ] AWS credentials configured
- [ ] Database migrations run
- [ ] Frontend builds successfully
- [ ] API documentation updated
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Monitoring configured
- [ ] Backup strategy in place

## 🎉 Success Indicators

- ✅ Backend starts without errors
- ✅ Frontend loads correctly
- ✅ Can login and create batches
- ✅ QR generation works
- ✅ QR scanning works
- ✅ Verification displays correctly
- ✅ AWS services respond
- ✅ Database queries work
- ✅ API docs accessible
- ✅ All endpoints return 200

---

**Quick Help**: See START_HERE.md for detailed instructions
