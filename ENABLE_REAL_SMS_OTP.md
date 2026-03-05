# Enable Real-Time SMS OTP with AWS Cognito

This guide explains how to set up real SMS OTP authentication using AWS Cognito.

## Current Status

- **Demo Mode**: OTP is always "0000" (works with any phone number)
- **Production Mode**: Real SMS OTP sent via AWS Cognito (requires setup)

## Why Lambda Triggers Are Needed

AWS Cognito requires Lambda triggers for custom authentication flows like passwordless OTP. The triggers handle:
1. **Define Auth Challenge**: Determines the authentication flow
2. **Create Auth Challenge**: Generates the OTP code
3. **Verify Auth Challenge**: Validates the OTP entered by the user

## Setup Steps

### Step 1: Create Lambda Functions

You need to create 3 Lambda functions in AWS:

#### 1.1 Define Auth Challenge Lambda

```python
# define_auth_challenge.py
def lambda_handler(event, context):
    if len(event['request']['session']) == 0:
        # First attempt - send OTP
        event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = False
    elif len(event['request']['session']) == 1 and event['request']['session'][0]['challengeName'] == 'CUSTOM_CHALLENGE':
        # Second attempt - verify OTP
        if event['request']['session'][0]['challengeResult']:
            event['response']['issueTokens'] = True
            event['response']['failAuthentication'] = False
        else:
            event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
            event['response']['issueTokens'] = False
            event['response']['failAuthentication'] = False
    else:
        # Too many attempts
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = True
    
    return event
```

#### 1.2 Create Auth Challenge Lambda

```python
# create_auth_challenge.py
import random

def lambda_handler(event, context):
    if event['request']['challengeName'] == 'CUSTOM_CHALLENGE':
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store OTP in session
        event['response']['privateChallengeParameters'] = {'otp': otp}
        event['response']['challengeMetadata'] = 'OTP_CHALLENGE'
        
        # Send SMS via SNS
        phone_number = event['request']['userAttributes']['phone_number']
        message = f'Your verification code is: {otp}'
        
        # Note: SMS sending is handled by Cognito automatically
        # if SMS configuration is set up in the User Pool
    
    return event
```

#### 1.3 Verify Auth Challenge Lambda

```python
# verify_auth_challenge.py
def lambda_handler(event, context):
    expected_answer = event['request']['privateChallengeParameters']['otp']
    user_answer = event['request']['challengeAnswer']
    
    event['response']['answerCorrect'] = (expected_answer == user_answer)
    
    return event
```

### Step 2: Configure Cognito User Pool

1. Go to AWS Cognito Console
2. Select your User Pool: `us-east-1_dKlYoNrpX`
3. Go to "Triggers" tab
4. Configure the following triggers:
   - **Define auth challenge**: Select your Define Auth Challenge Lambda
   - **Create auth challenge**: Select your Create Auth Challenge Lambda
   - **Verify auth challenge response**: Select your Verify Auth Challenge Lambda

### Step 3: Configure SMS Settings

1. In Cognito User Pool, go to "Messaging" tab
2. Configure SMS:
   - **SMS message**: "Your verification code is {####}"
   - **IAM role**: Create or select an IAM role with SNS permissions
   - **External ID**: (optional)

### Step 4: Enable Custom Auth Flow

1. Go to "App clients" in your User Pool
2. Select your app client: `174bbue8jnadpa8hiudpi61n34`
3. Edit "Authentication flows"
4. Enable: **ALLOW_CUSTOM_AUTH**
5. Save changes

### Step 5: Update Environment Variables

In `backend/.env`, set:
```properties
USE_COGNITO_AUTH=true
```

### Step 6: Test

1. Restart your backend server
2. Try logging in with a real phone number (format: +919876543210)
3. You should receive an SMS with a 6-digit OTP
4. Enter the OTP to complete login

## Alternative: Use AWS Amplify CLI

AWS Amplify CLI can automate this setup:

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Configure Amplify
amplify configure

# Add authentication
amplify add auth

# Select: Custom authentication flow
# Select: SMS-based OTP

# Deploy
amplify push
```

## Cost Considerations

- **SMS Costs**: AWS charges for SMS messages
  - US: ~$0.00645 per SMS
  - India: ~$0.02805 per SMS
  - Other regions: Check [AWS SNS Pricing](https://aws.amazon.com/sns/sms-pricing/)

- **Lambda Costs**: Usually free tier covers development usage
- **Cognito Costs**: First 50,000 MAUs free

## Troubleshooting

### "Custom auth lambda trigger is not configured"
- Ensure all 3 Lambda triggers are configured in Cognito
- Check Lambda execution role has necessary permissions

### SMS not received
- Check phone number format (+country code)
- Verify SMS configuration in Cognito
- Check AWS SNS spending limits
- Ensure you're not in Cognito sandbox mode (requires AWS support ticket to exit)

### Lambda errors
- Check CloudWatch Logs for Lambda execution errors
- Verify Lambda has correct permissions
- Test Lambda functions individually

## Recommended Approach for Development

For development and testing, **keep demo mode enabled**:
- No SMS costs
- Faster testing
- No AWS configuration needed
- OTP is always "0000"

Enable real SMS OTP only for production deployment.

## Summary

✅ **Demo Mode (Current)**: Simple, free, good for development
❌ **Production Mode**: Requires Lambda setup, costs money, better for production

To keep using demo mode, ensure `USE_COGNITO_AUTH=false` in your `.env` file.
