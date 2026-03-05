# Cognito Lambda Functions for SMS OTP

This directory contains the Lambda functions needed for AWS Cognito custom authentication with SMS OTP.

## Files

- `define_auth_challenge.py` - Determines the authentication flow
- `create_auth_challenge.py` - Generates OTP and sends SMS
- `verify_auth_challenge.py` - Verifies the OTP entered by user
- `deploy.sh` - Automated deployment script

## Quick Setup

### Prerequisites

1. AWS CLI installed and configured
2. AWS credentials with permissions for:
   - Lambda (create functions, update code)
   - IAM (create roles, attach policies)
   - Cognito (update user pool)
   - SNS (publish SMS)

### Deployment Steps

1. **Navigate to this directory:**
   ```bash
   cd cognito-lambdas
   ```

2. **Make the deploy script executable:**
   ```bash
   chmod +x deploy.sh
   ```

3. **Run the deployment script:**
   ```bash
   ./deploy.sh
   ```

4. **Enable Cognito auth in your backend:**
   Edit `backend/.env`:
   ```properties
   USE_COGNITO_AUTH=true
   ```

5. **Restart your backend server:**
   ```bash
   cd ../backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Manual Setup (Alternative)

If you prefer to set up manually via AWS Console:

### Step 1: Create Lambda Functions

1. Go to AWS Lambda Console
2. Create 3 new functions with Python 3.11 runtime:
   - `Farm2Fork-DefineAuthChallenge`
   - `Farm2Fork-CreateAuthChallenge`
   - `Farm2Fork-VerifyAuthChallenge`

3. Copy the code from the respective `.py` files

4. Create an IAM role with:
   - `AWSLambdaBasicExecutionRole` policy
   - SNS publish permissions

### Step 2: Configure Cognito

1. Go to AWS Cognito Console
2. Select your User Pool: `us-east-1_dKlYoNrpX`
3. Go to "Triggers" tab
4. Configure:
   - **Define auth challenge**: Select `Farm2Fork-DefineAuthChallenge`
   - **Create auth challenge**: Select `Farm2Fork-CreateAuthChallenge`
   - **Verify auth challenge response**: Select `Farm2Fork-VerifyAuthChallenge`

### Step 3: Enable Custom Auth

1. Go to "App clients" in your User Pool
2. Select your app client
3. Edit "Authentication flows"
4. Enable: `ALLOW_CUSTOM_AUTH`
5. Save changes

## Testing

1. **Test OTP request:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/request-otp \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "+919876543210"}'
   ```

2. **Check your phone for SMS**

3. **Test OTP verification:**
   ```bash
   curl -X POST http://localhost:8000/api/auth/verify-otp \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "+919876543210", "otp": "123456", "name": "Test User"}'
   ```

## Troubleshooting

### Lambda not being invoked
- Check CloudWatch Logs for Lambda execution
- Verify Lambda permissions allow Cognito to invoke
- Check User Pool trigger configuration

### SMS not received
- Verify phone number format (+country code)
- Check AWS SNS spending limits
- Ensure you're not in Cognito sandbox mode
- Check Lambda logs for SMS sending errors

### "Custom auth lambda trigger is not configured"
- Ensure all 3 Lambda triggers are configured in Cognito
- Verify Lambda ARNs are correct
- Check Lambda execution role has necessary permissions

## Cost Considerations

- **SMS**: ~$0.02805 per SMS (India), varies by region
- **Lambda**: Usually covered by free tier
- **Cognito**: First 50,000 MAUs free

## Rollback to Demo Mode

If you want to go back to demo mode:

1. Edit `backend/.env`:
   ```properties
   USE_COGNITO_AUTH=false
   ```

2. Restart backend server

Demo mode uses OTP "0000" and doesn't send real SMS.
