# Authentication Modes Guide

## Current Status
✅ Your application is currently in **DEMO MODE** with OTP: `0000`

## Two Authentication Modes

### 1. Demo Mode (Current) ✅
**Best for**: Development, testing, demos

**Configuration**:
```env
USE_COGNITO_AUTH=false
```

**How it works**:
- Any phone number can login
- OTP is always `0000`
- No SMS sent
- No AWS Cognito required
- Perfect for local development

**To use**:
1. Enter any 10-digit phone number
2. Enter OTP: `0000`
3. Login successful!

---

### 2. Production Mode (Cognito SMS OTP)
**Best for**: Production deployment, real users

**Configuration**:
```env
USE_COGNITO_AUTH=true
COGNITO_USER_POOL_ID=us-east-1_dKlYoNrpX
COGNITO_CLIENT_ID=52i9h3ah7adek4p7giq3iub17n
COGNITO_CLIENT_SECRET=tssdc3a940sfnqh76i5snvrv5rlnadukhscmvvik3fpi1oqrn6i
COGNITO_REGION=us-east-1
```

**How it works**:
- Real SMS OTP sent to phone number
- 6-digit OTP code
- OTP expires after 3 minutes
- Requires AWS Cognito User Pool setup
- Requires Lambda triggers for custom auth flow

**Prerequisites**:
1. AWS Cognito User Pool created
2. Lambda triggers configured (Define Auth, Create Auth, Verify Auth)
3. SNS permissions for SMS sending
4. Phone numbers must be valid and able to receive SMS

---

## How to Switch Modes

### Switch to Demo Mode (Current)
1. Open `backend/.env`
2. Set: `USE_COGNITO_AUTH=false`
3. Restart backend server
4. Use OTP: `0000` to login

### Switch to Production Mode
1. **Setup AWS Cognito** (follow `docs/cognito-authentication.md`)
2. Open `backend/.env`
3. Set: `USE_COGNITO_AUTH=true`
4. Add Cognito credentials:
   ```env
   COGNITO_USER_POOL_ID=us-east-1_dKlYoNrpX
   COGNITO_CLIENT_ID=52i9h3ah7adek4p7giq3iub17n
   COGNITO_CLIENT_SECRET=tssdc3a940sfnqh76i5snvrv5rlnadukhscmvvik3fpi1oqrn6i
   COGNITO_REGION=us-east-1
   ```
5. Restart backend server
6. Real SMS OTP will be sent

---

## Testing Production Mode

### Verify Cognito Setup
Run the verification script:
```bash
cd backend
python setup_cognito.py
```

This will check:
- ✅ Cognito credentials are valid
- ✅ User Pool exists
- ✅ Lambda triggers are configured
- ✅ SNS permissions for SMS

### Test SMS OTP Flow

#### Step 1: Request OTP
```bash
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

**Expected Response**:
```json
{
  "success": true,
  "message": "OTP sent successfully via SMS",
  "session": "session-token-here"
}
```

#### Step 2: Check Phone for SMS
You should receive an SMS with a 6-digit OTP code.

#### Step 3: Verify OTP
```bash
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "otp": "123456",
    "session": "session-token-here",
    "name": "Test Farmer"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "token": "jwt-token-here",
  "farmer_id": "uuid",
  "farmer_name": "Test Farmer",
  "is_new_user": true
}
```

---

## Frontend Integration

The frontend automatically adapts to both modes:

### Demo Mode
- Shows: "Demo mode: Use OTP 0000"
- Single-step login form
- No OTP request step

### Production Mode (Future)
- Two-step flow:
  1. Enter phone → Request OTP
  2. Enter OTP → Verify and login
- Shows "Resend OTP" button
- OTP expiration timer

---

## Current Configuration

Your `.env` file currently has:
```env
USE_COGNITO_AUTH=false  # Demo mode active
```

Your `.env.example` has Cognito credentials ready:
```env
USE_COGNITO_AUTH=false
COGNITO_USER_POOL_ID=us-east-1_dKlYoNrpX
COGNITO_CLIENT_ID=52i9h3ah7adek4p7giq3iub17n
COGNITO_CLIENT_SECRET=tssdc3a940sfnqh76i5snvrv5rlnadukhscmvvik3fpi1oqrn6i
```

---

## Troubleshooting

### Demo Mode Issues
**Problem**: OTP 0000 not working
**Solution**: 
- Check `USE_COGNITO_AUTH=false` in `.env`
- Restart backend server
- Clear browser cache

### Production Mode Issues

**Problem**: SMS not received
**Solutions**:
1. Check AWS SNS permissions
2. Verify phone number format (+country code)
3. Check AWS SNS spending limits
4. Verify Lambda triggers are deployed

**Problem**: "Invalid OTP" error
**Solutions**:
1. Check OTP hasn't expired (3 min limit)
2. Verify correct session token used
3. Check Lambda Verify Auth trigger logs

**Problem**: "Failed to send OTP"
**Solutions**:
1. Run `python setup_cognito.py` to verify setup
2. Check Cognito User Pool exists
3. Verify AWS credentials have Cognito permissions
4. Check CloudWatch logs for Lambda errors

---

## Cost Considerations

### Demo Mode
- **Cost**: $0 (no AWS services used for auth)
- **SMS**: None sent

### Production Mode
- **Cognito**: Free tier includes 50,000 MAUs
- **SMS**: ~$0.00645 per SMS (varies by country)
- **Lambda**: Free tier includes 1M requests/month
- **Estimate**: ~$0.01 per user login (SMS cost)

---

## Security Notes

### Demo Mode
⚠️ **NOT for production use**
- Anyone can login with any phone number
- No real authentication
- Use only for development/testing

### Production Mode
✅ **Production ready**
- Real phone verification
- OTP expires after 3 minutes
- Rate limiting via Cognito
- Secure JWT tokens
- Phone number verified

---

## Quick Reference

| Feature | Demo Mode | Production Mode |
|---------|-----------|-----------------|
| OTP | Always `0000` | Real 6-digit SMS |
| Phone Verification | No | Yes |
| SMS Cost | $0 | ~$0.01/login |
| Setup Required | None | Cognito + Lambda |
| Security | Low | High |
| Best For | Development | Production |

---

## Next Steps

### To Stay in Demo Mode
✅ Nothing to do! You're all set.

### To Enable Production Mode
1. Read `docs/cognito-authentication.md`
2. Create AWS Cognito User Pool
3. Deploy Lambda triggers
4. Update `.env` with Cognito credentials
5. Set `USE_COGNITO_AUTH=true`
6. Test with `python setup_cognito.py`
7. Update frontend for two-step OTP flow

---

## Support

For detailed Cognito setup instructions, see:
- `docs/cognito-authentication.md` - Complete setup guide
- `COGNITO_UPGRADE_SUMMARY.md` - Implementation overview
- `backend/setup_cognito.py` - Verification script
- `backend/cognito_service.py` - Service implementation
