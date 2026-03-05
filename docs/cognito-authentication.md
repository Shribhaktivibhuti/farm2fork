# AWS Cognito SMS OTP Authentication Setup Guide

This guide explains how to set up AWS Cognito for production-ready SMS OTP authentication in the FARM2FORK platform.

## Overview

The system supports two authentication modes:
- **Demo Mode** (default): Uses OTP "0000" for testing
- **Production Mode**: Uses AWS Cognito with real SMS OTP

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Access to AWS Console
- Phone number for testing (with SMS capability)

## Step 1: Create Cognito User Pool

### Using AWS Console

1. **Navigate to Amazon Cognito**
   - Go to AWS Console → Services → Cognito
   - Click "Create user pool"

2. **Configure Sign-in Experience**
   - Sign-in options: Select **"Phone number"**
   - Cognito user pool sign-in options: Check **"Phone number"**
   - Click "Next"

3. **Configure Security Requirements**
   - Password policy: Select "Cognito defaults" (not used for phone auth)
   - Multi-factor authentication: **"No MFA"** (OTP is the primary auth)
   - User account recovery: Select **"Enable self-service account recovery"**
   - Recovery method: **"Phone number only"**
   - Click "Next"

4. **Configure Sign-up Experience**
   - Self-service sign-up: **Enable**
   - Attribute verification: **"Allow Cognito to automatically send messages to verify"**
   - Verifying attribute changes: Check **"Phone number"**
   - Required attributes: Select **"phone_number"**
   - Click "Next"

5. **Configure Message Delivery**
   - Email provider: Select **"Send email with Amazon SES"** (or Cognito default)
   - SMS: Select **"Send SMS with Amazon SNS"**
   - IAM role: Create new role or select existing
   - Click "Next"

6. **Integrate Your App**
   - User pool name: `farm2fork-users`
   - App client name: `farm2fork-app`
   - Client secret: **Generate a client secret**
   - Authentication flows: Check **"ALLOW_CUSTOM_AUTH"**
   - Click "Next"

7. **Review and Create**
   - Review all settings
   - Click "Create user pool"

### Using AWS CLI

```bash
# Create user pool
aws cognito-idp create-user-pool \
  --pool-name farm2fork-users \
  --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=false,RequireLowercase=false,RequireNumbers=false,RequireSymbols=false}" \
  --auto-verified-attributes phone_number \
  --sms-authentication-message "Your FARM2FORK verification code is {####}" \
  --mfa-configuration OFF \
  --schema Name=phone_number,AttributeDataType=String,Required=true,Mutable=true \
  --region us-east-1

# Create app client
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_XXXXXXXXX \
  --client-name farm2fork-app \
  --generate-secret \
  --explicit-auth-flows ALLOW_CUSTOM_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --region us-east-1
```

## Step 2: Configure SMS Settings

### Enable SMS in AWS Account

1. **Request SMS Spending Limit Increase**
   - Go to AWS Support Center
   - Create case: "Service limit increase"
   - Limit type: "SNS Text Messaging"
   - Region: Your region
   - Limit: "Account spending limit"
   - New limit: $10 (or as needed)

2. **Configure SNS for SMS**
   ```bash
   # Set default SMS type to Transactional
   aws sns set-sms-attributes \
     --attributes DefaultSMSType=Transactional \
     --region us-east-1
   ```

3. **Verify SMS Sandbox** (for testing)
   - Go to SNS Console → Text messaging (SMS) → Sandbox destination phone numbers
   - Add your test phone number
   - Verify the phone number

### SMS Cost Estimation

- India: $0.00645 per SMS
- USA: $0.00645 per SMS
- Monthly estimate for 1000 users: ~$6.45

## Step 3: Create Lambda Triggers (Custom Auth Flow)

Cognito requires Lambda triggers for custom authentication flow.

### Create Define Auth Challenge Lambda

```python
# lambda/define_auth_challenge.py
def lambda_handler(event, context):
    if len(event['request']['session']) == 0:
        # First attempt - send OTP
        event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = False
    elif len(event['request']['session']) == 1 and \
         event['request']['session'][0]['challengeName'] == 'CUSTOM_CHALLENGE':
        # Second attempt - verify OTP
        if event['request']['session'][0]['challengeResult']:
            event['response']['issueTokens'] = True
            event['response']['failAuthentication'] = False
        else:
            event['response']['issueTokens'] = False
            event['response']['failAuthentication'] = True
    else:
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = True
    
    return event
```

### Create Create Auth Challenge Lambda

```python
# lambda/create_auth_challenge.py
import random

def lambda_handler(event, context):
    if event['request']['challengeName'] == 'CUSTOM_CHALLENGE':
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        event['response']['publicChallengeParameters'] = {}
        event['response']['privateChallengeParameters'] = {'answer': otp}
        event['response']['challengeMetadata'] = 'OTP_CHALLENGE'
        
        # Send SMS via SNS
        phone_number = event['request']['userAttributes']['phone_number']
        message = f"Your FARM2FORK verification code is: {otp}"
        
        import boto3
        sns = boto3.client('sns')
        sns.publish(
            PhoneNumber=phone_number,
            Message=message
        )
    
    return event
```

### Create Verify Auth Challenge Lambda

```python
# lambda/verify_auth_challenge.py
def lambda_handler(event, context):
    expected_answer = event['request']['privateChallengeParameters']['answer']
    user_answer = event['request']['challengeAnswer']
    
    event['response']['answerCorrect'] = (expected_answer == user_answer)
    
    return event
```

### Deploy Lambda Functions

```bash
# Create IAM role for Lambda
aws iam create-role \
  --role-name CognitoLambdaRole \
  --assume-role-policy-document file://trust-policy.json

# Attach SNS publish policy
aws iam attach-role-policy \
  --role-name CognitoLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSNSFullAccess

# Create Lambda functions
aws lambda create-function \
  --function-name DefineAuthChallenge \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT_ID:role/CognitoLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://define_auth_challenge.zip

# Repeat for other Lambda functions
```

### Attach Lambda Triggers to User Pool

```bash
aws cognito-idp update-user-pool \
  --user-pool-id us-east-1_XXXXXXXXX \
  --lambda-config \
    DefineAuthChallenge=arn:aws:lambda:us-east-1:ACCOUNT_ID:function:DefineAuthChallenge,\
    CreateAuthChallenge=arn:aws:lambda:us-east-1:ACCOUNT_ID:function:CreateAuthChallenge,\
    VerifyAuthChallengeResponse=arn:aws:lambda:us-east-1:ACCOUNT_ID:function:VerifyAuthChallenge
```

## Step 4: Configure IAM Permissions

### Required IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cognito-idp:InitiateAuth",
        "cognito-idp:RespondToAuthChallenge",
        "cognito-idp:AdminCreateUser",
        "cognito-idp:AdminGetUser",
        "cognito-idp:GetUser"
      ],
      "Resource": "arn:aws:cognito-idp:us-east-1:ACCOUNT_ID:userpool/us-east-1_XXXXXXXXX"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "*"
    }
  ]
}
```

## Step 5: Update Backend Configuration

### Update `.env` File

```bash
# Enable Cognito authentication
USE_COGNITO_AUTH=true

# Add Cognito configuration
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=your-app-client-id
COGNITO_CLIENT_SECRET=your-app-client-secret
COGNITO_JWKS_URL=https://cognito-idp.us-east-1.amazonaws.com/us-east-1_XXXXXXXXX/.well-known/jwks.json
```

### Install Required Dependencies

```bash
cd backend
pip install python-jose[cryptography] requests
```

## Step 6: Testing

### Test with Demo Mode (Development)

```bash
# Keep USE_COGNITO_AUTH=false in .env
# Use OTP: 0000
```

### Test with Cognito (Production)

```bash
# Set USE_COGNITO_AUTH=true in .env
# Use real phone number: +919876543210
# Enter OTP received via SMS
```

### API Testing with cURL

```bash
# Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'

# Verify OTP
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "otp": "123456",
    "session": "session-token-from-previous-response"
  }'
```

## Troubleshooting

### Common Issues

1. **SMS Not Received**
   - Check SNS sandbox settings
   - Verify phone number is verified in SNS
   - Check AWS account SMS spending limit
   - Verify Lambda function logs in CloudWatch

2. **Invalid OTP Error**
   - OTP expires after 3 minutes
   - Check Lambda function is generating OTP correctly
   - Verify SNS is sending SMS

3. **Token Validation Fails**
   - Check JWKS URL is correct
   - Verify token hasn't expired
   - Check client ID matches

4. **User Creation Fails**
   - Verify phone number format (+country code)
   - Check IAM permissions
   - Review CloudWatch logs

### Enable Debug Logging

```python
# In backend/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Best Practices

1. **Never commit secrets to Git**
   - Use environment variables
   - Use AWS Secrets Manager for production

2. **Enable MFA for AWS Console**
   - Protect your AWS account

3. **Rotate Client Secrets**
   - Rotate every 90 days

4. **Monitor SMS Costs**
   - Set up CloudWatch alarms
   - Monitor SNS spending

5. **Rate Limiting**
   - Implement rate limiting on OTP requests
   - Prevent SMS bombing attacks

## Cost Optimization

1. **Use Demo Mode for Development**
   - Save SMS costs during development

2. **Implement OTP Caching**
   - Cache OTP for 3 minutes
   - Reduce duplicate SMS sends

3. **Monitor Usage**
   - Track authentication attempts
   - Identify unusual patterns

## Production Deployment

### Environment Variables

```bash
# Production .env
USE_COGNITO_AUTH=true
COGNITO_USER_POOL_ID=us-east-1_PROD_POOL
COGNITO_CLIENT_ID=prod-client-id
COGNITO_CLIENT_SECRET=prod-client-secret
ENVIRONMENT=production
```

### Health Check

```bash
# Verify Cognito connectivity
curl http://your-api.com/health
```

## Support

For issues or questions:
- AWS Cognito Documentation: https://docs.aws.amazon.com/cognito/
- AWS Support: https://console.aws.amazon.com/support/
- Project Issues: [Your GitHub Issues]

## References

- [AWS Cognito Custom Authentication Flow](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-authentication-flow.html#amazon-cognito-user-pools-custom-authentication-flow)
- [AWS SNS SMS Pricing](https://aws.amazon.com/sns/sms-pricing/)
- [JWT Token Validation](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html)
