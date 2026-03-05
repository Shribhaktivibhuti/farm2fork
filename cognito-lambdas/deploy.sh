#!/bin/bash

# Cognito Lambda Deployment Script
# This script creates and deploys the Lambda functions for Cognito custom auth

set -e

echo "========================================="
echo "Cognito Lambda Deployment Script"
echo "========================================="

# Configuration
REGION="us-east-1"
USER_POOL_ID="us-east-1_dKlYoNrpX"
APP_CLIENT_ID="174bbue8jnadpa8hiudpi61n34"

# Lambda function names
DEFINE_AUTH_FUNCTION="Farm2Fork-DefineAuthChallenge"
CREATE_AUTH_FUNCTION="Farm2Fork-CreateAuthChallenge"
VERIFY_AUTH_FUNCTION="Farm2Fork-VerifyAuthChallenge"

# IAM role name
LAMBDA_ROLE_NAME="Farm2Fork-CognitoLambdaRole"

echo ""
echo "Step 1: Creating IAM role for Lambda functions..."
echo "=================================================="

# Create IAM role trust policy
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create IAM role
aws iam create-role \
  --role-name $LAMBDA_ROLE_NAME \
  --assume-role-policy-document file://trust-policy.json \
  --region $REGION \
  2>/dev/null || echo "Role already exists"

# Attach basic Lambda execution policy
aws iam attach-role-policy \
  --role-name $LAMBDA_ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  --region $REGION

# Create and attach SNS policy for sending SMS
cat > sns-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name $LAMBDA_ROLE_NAME \
  --policy-name SNSPublishPolicy \
  --policy-document file://sns-policy.json \
  --region $REGION

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $LAMBDA_ROLE_NAME --query 'Role.Arn' --output text)
echo "✅ IAM Role created: $ROLE_ARN"

# Wait for role to be available
echo "Waiting for IAM role to propagate..."
sleep 10

echo ""
echo "Step 2: Creating Lambda functions..."
echo "====================================="

# Function to create Lambda
create_lambda() {
    local FUNCTION_NAME=$1
    local PYTHON_FILE=$2
    
    echo "Creating $FUNCTION_NAME..."
    
    # Create deployment package
    zip ${FUNCTION_NAME}.zip ${PYTHON_FILE}
    
    # Create or update Lambda function
    aws lambda create-function \
      --function-name $FUNCTION_NAME \
      --runtime python3.11 \
      --role $ROLE_ARN \
      --handler ${PYTHON_FILE%.py}.lambda_handler \
      --zip-file fileb://${FUNCTION_NAME}.zip \
      --region $REGION \
      --timeout 10 \
      --memory-size 128 \
      2>/dev/null || \
    aws lambda update-function-code \
      --function-name $FUNCTION_NAME \
      --zip-file fileb://${FUNCTION_NAME}.zip \
      --region $REGION
    
    echo "✅ $FUNCTION_NAME created/updated"
    
    # Clean up zip file
    rm ${FUNCTION_NAME}.zip
}

# Create all three Lambda functions
create_lambda $DEFINE_AUTH_FUNCTION "define_auth_challenge.py"
create_lambda $CREATE_AUTH_FUNCTION "create_auth_challenge.py"
create_lambda $VERIFY_AUTH_FUNCTION "verify_auth_challenge.py"

echo ""
echo "Step 3: Configuring Cognito User Pool triggers..."
echo "=================================================="

# Get Lambda ARNs
DEFINE_ARN=$(aws lambda get-function --function-name $DEFINE_AUTH_FUNCTION --region $REGION --query 'Configuration.FunctionArn' --output text)
CREATE_ARN=$(aws lambda get-function --function-name $CREATE_AUTH_FUNCTION --region $REGION --query 'Configuration.FunctionArn' --output text)
VERIFY_ARN=$(aws lambda get-function --function-name $VERIFY_AUTH_FUNCTION --region $REGION --query 'Configuration.FunctionArn' --output text)

# Add Lambda permissions for Cognito to invoke
aws lambda add-permission \
  --function-name $DEFINE_AUTH_FUNCTION \
  --statement-id CognitoInvoke \
  --action lambda:InvokeFunction \
  --principal cognito-idp.amazonaws.com \
  --source-arn arn:aws:cognito-idp:${REGION}:$(aws sts get-caller-identity --query Account --output text):userpool/${USER_POOL_ID} \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

aws lambda add-permission \
  --function-name $CREATE_AUTH_FUNCTION \
  --statement-id CognitoInvoke \
  --action lambda:InvokeFunction \
  --principal cognito-idp.amazonaws.com \
  --source-arn arn:aws:cognito-idp:${REGION}:$(aws sts get-caller-identity --query Account --output text):userpool/${USER_POOL_ID} \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

aws lambda add-permission \
  --function-name $VERIFY_AUTH_FUNCTION \
  --statement-id CognitoInvoke \
  --action lambda:InvokeFunction \
  --principal cognito-idp.amazonaws.com \
  --source-arn arn:aws:cognito-idp:${REGION}:$(aws sts get-caller-identity --query Account --output text):userpool/${USER_POOL_ID} \
  --region $REGION \
  2>/dev/null || echo "Permission already exists"

# Update User Pool with Lambda triggers
aws cognito-idp update-user-pool \
  --user-pool-id $USER_POOL_ID \
  --lambda-config DefineAuthChallenge=$DEFINE_ARN,CreateAuthChallenge=$CREATE_ARN,VerifyAuthChallengeResponse=$VERIFY_ARN \
  --region $REGION

echo "✅ Cognito User Pool triggers configured"

echo ""
echo "Step 4: Enabling CUSTOM_AUTH flow in App Client..."
echo "==================================================="

# Update app client to allow custom auth
aws cognito-idp update-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-id $APP_CLIENT_ID \
  --explicit-auth-flows ALLOW_CUSTOM_AUTH ALLOW_REFRESH_TOKEN_AUTH \
  --region $REGION

echo "✅ App Client configured for custom auth"

# Clean up temporary files
rm -f trust-policy.json sns-policy.json

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "Lambda Functions Created:"
echo "  - $DEFINE_AUTH_FUNCTION"
echo "  - $CREATE_AUTH_FUNCTION"
echo "  - $VERIFY_AUTH_FUNCTION"
echo ""
echo "Next Steps:"
echo "1. Set USE_COGNITO_AUTH=true in backend/.env"
echo "2. Restart your backend server"
echo "3. Test with a real phone number (format: +919876543210)"
echo ""
echo "Note: SMS costs will apply for each OTP sent"
echo ""
