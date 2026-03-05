# FARM2FORK Troubleshooting Guide

## Issue: "Failed to fetch" on Login Page

### ✅ Backend Status: WORKING
The backend is running correctly at http://localhost:8000 and responding to requests.

### Diagnosis Steps

#### 1. Check Frontend Dev Server
```bash
# Open a new terminal
cd frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in XXX ms
➜  Local:   http://localhost:5174/
```

#### 2. Verify Backend is Accessible
Open a new browser tab and go to:
- http://localhost:8000/health

**Expected response:**
```json
{
  "status": "healthy",
  "service": "FARM2FORK API",
  "version": "1.0.0",
  "database": "configured",
  "aws_services": "configured"
}
```

#### 3. Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try to login again
4. Look for error messages

**Common errors:**
- `net::ERR_CONNECTION_REFUSED` → Backend not running
- `CORS error` → CORS misconfiguration
- `Failed to fetch` → Network issue or wrong URL

#### 4. Test API Directly
Open browser console and run:
```javascript
fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({phone: '1234567890', otp: '0000'})
})
.then(r => r.json())
.then(d => console.log('Success:', d))
.catch(e => console.error('Error:', e))
```

### Solutions

#### Solution 1: Restart Frontend
```bash
# Stop frontend (Ctrl+C)
cd frontend
npm install html5-qrcode  # Make sure this is installed
npm run dev
```

#### Solution 2: Clear Browser Cache
1. Open DevTools (F12)
2. Right-click on refresh button
3. Select "Empty Cache and Hard Reload"

#### Solution 3: Check Firewall
Windows Firewall might be blocking the connection:
1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Find Node.js and Python
4. Make sure both Private and Public are checked

#### Solution 4: Use Different Browser
Try Chrome, Firefox, or Edge to rule out browser-specific issues.

#### Solution 5: Check CORS Configuration
The backend CORS is configured for:
- http://localhost:5173
- http://localhost:5174
- http://localhost:3000

If your frontend is on a different port, update `backend/.env`:
```bash
CORS_ORIGINS=http://localhost:YOUR_PORT,http://localhost:5174
```

Then restart backend:
```bash
cd backend
# Stop with Ctrl+C
uvicorn main:app --reload
```

### Quick Test Commands

#### Test Backend Health
```bash
curl http://localhost:8000/health
```

#### Test Login Endpoint
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"1234567890\",\"otp\":\"0000\"}"
```

#### Check What's Running on Ports
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5174

# Should show processes listening on these ports
```

### Current System Status

✅ **Backend**: Running on http://localhost:8000
- Health check: PASS
- Login endpoint: PASS
- CORS: Configured for localhost:5174

❓ **Frontend**: Status unknown
- Expected: http://localhost:5174
- Action: Start with `cd frontend && npm run dev`

✅ **Database**: Working
- SQLite database initialized
- 1 farmer, 1 batch in database

### Step-by-Step Fix

1. **Open Terminal 1** (Backend - already running ✅)
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Open Terminal 2** (Frontend - needs to start)
   ```bash
   cd frontend
   npm install html5-qrcode
   npm run dev
   ```

3. **Open Browser**
   - Go to http://localhost:5174
   - Try login again
   - Phone: 1234567890
   - OTP: 0000

### If Still Not Working

#### Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Try to login
4. Look for the POST request to `/api/auth/login`
5. Check:
   - Status code (should be 200)
   - Response (should have token)
   - Headers (check CORS headers)

#### Enable Verbose Logging
Add this to browser console:
```javascript
// Override fetch to log all requests
const originalFetch = window.fetch;
window.fetch = function(...args) {
  console.log('Fetch:', args);
  return originalFetch.apply(this, args)
    .then(response => {
      console.log('Response:', response);
      return response;
    })
    .catch(error => {
      console.error('Fetch error:', error);
      throw error;
    });
};
```

### Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Connection refused | Backend not running | Start backend: `uvicorn main:app --reload` |
| CORS error | Wrong origin | Update CORS_ORIGINS in .env |
| 404 Not Found | Wrong URL | Check URL is http://localhost:8000 |
| Failed to fetch | Network issue | Check firewall, try different browser |
| Blank page | Frontend not running | Start frontend: `npm run dev` |

### Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5174
- [ ] Can access http://localhost:8000/health
- [ ] Can access http://localhost:5174
- [ ] Browser console shows no errors
- [ ] Network tab shows successful requests

### Get More Help

1. **Check logs**: Look at terminal output for errors
2. **Read docs**: See START_HERE.md for setup
3. **Test API**: Use Postman collection
4. **Verify setup**: Run `python verify_system.py`

### Emergency Reset

If nothing works, reset everything:

```bash
# Stop all processes (Ctrl+C in all terminals)

# Backend
cd backend
rm farm2fork.db
python init_db.py
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
rm -rf node_modules
npm install
npm install html5-qrcode
npm run dev
```

### Contact Information

If you're still stuck:
1. Check all terminals for error messages
2. Look at browser console for errors
3. Verify both servers are running
4. Try the curl commands to test backend directly

---

**Most Common Solution**: Just start the frontend dev server!
```bash
cd frontend && npm run dev
```
