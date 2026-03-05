# Farm2Fork - Quick Start Guide

## 🚀 Start the Application

### Terminal 1 - Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## 🌐 Access URLs

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔑 Test Credentials

- **Phone**: Any 10-digit number (e.g., 9876543210)
- **OTP**: 0000

## ✅ System Status

All systems operational! See `CURRENT_STATUS.md` for details.

## 🔧 Quick Fixes

### Backend won't start?
```bash
cd backend
uvicorn main:app --reload --port 8000
```
(Use uvicorn, NOT `python main.py`)

### Port in use?
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## 📚 Documentation

- `CURRENT_STATUS.md` - Full system status
- `FIXES_APPLIED.md` - What was fixed
- `AWS_BEDROCK_SETUP.md` - Enable AI features
- `TROUBLESHOOTING.md` - Common issues

## 🎯 Test Flow

1. Login with phone + OTP "0000"
2. Create a batch with crop details
3. Generate QR code
4. Scan QR to verify as consumer

## 💡 Key Features

✅ Authentication  
✅ Batch creation  
✅ Image upload (S3)  
✅ OCR extraction (Textract)  
✅ QR generation  
✅ Consumer verification  
✅ Safety analysis (fallback mode)  
✅ Multi-language support  

🟡 AI analysis (requires Bedrock approval - see AWS_BEDROCK_SETUP.md)

---

**Everything is working! Start testing now.** 🎉
