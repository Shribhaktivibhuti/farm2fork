"""
Cognito Lambda Deployment Script using Python/Boto3
This script creates and deploys the Lambda functions for Cognito custom auth
"""

import boto3
import json
import zipfile
import time
import os
from botocore.exceptions import ClientError

# Configuration
REGION = "us-east-1"
USER_POOL_ID = "us-east-1_dKlYoNrpX"
APP_CLIENT_ID = "174bbue8jnadpa8hiudpi61n34"

# Lambda function names
DEFINE_AUTH_FUNCTION = "Farm2Fork-DefineAuthChallenge"
CREATE_AUTH_FUNCTION = "Farm2Fork-CreateAuthChallenge"
VERIFY_AUTH_FUNCTION = "Farm2Fork-VerifyAuthChallenge"

# IAM role name
LAMBDA_ROLE_NAME = "Farm2Fork-CognitoLambdaRole"

# AWS credentials from environment variables
# IMPORTANT: Set these as environment variables or use AWS CLI configuration
# Never hardcode credentials in production code!
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Initialize AWS clients
# If credentials are not in environment, boto3 will use AWS CLI configuration
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    iam = boto3.client('iam', region_name=REGION, 
                       aws_access_key_id=AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    lambda_client = boto3.client('lambda', region_name=REGION,
                                 aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    cognito = boto3.client('cognito-idp', region_name=REGION,
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    sts = boto3.client('sts', region_name=REGION,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
else:
    # Use default AWS CLI credentials
    iam = boto3.client('iam', region_name=REGION)
    lambda_client = boto3.client('lambda', region_name=REGION)
    cognito = boto3.client('cognito-idp', region_name=REGION)
    sts = boto3.client('sts', region_name=REGION)

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def create_iam_role():
    """Create IAM role for Lambda functions"""
    print_header("Step 1: Creating IAM role for Lambda functions")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        response = iam.create_role(
            RoleName=LAMBDA_ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Farm2Fork Cognito Lambda functions'
        )
        print(f"✅ IAM Role created: {response['Role']['Arn']}")
        role_arn = response['Role']['Arn']
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("⚠️  Role already exists, getting ARN...")
            response = iam.get_role(RoleName=LAMBDA_ROLE_NAME)
            role_arn = response['Role']['Arn']
            print(f"✅ Using existing role: {role_arn}")
        else:
            raise
    
    # Attach basic Lambda execution policy
    try:
        iam.attach_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        print("✅ Attached Lambda execution policy")
    except ClientError as e:
        if e.response['Error']['Code'] != 'EntityAlreadyExists':
            print(f"⚠️  Policy already attached or error: {e}")
    
    # Create and attach SNS policy
    sns_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["sns:Publish"],
                "Resource": "*"
            }
        ]
    }
    
    try:
        iam.put_role_policy(
            RoleName=LAMBDA_ROLE_NAME,
            PolicyName='SNSPublishPolicy',
            PolicyDocument=json.dumps(sns_policy)
        )
        print("✅ Attached SNS publish policy")
    except ClientError as e:
        print(f"⚠️  SNS policy error: {e}")
    
    # Wait for role to propagate
    print("⏳ Waiting for IAM role to propagate...")
    time.sleep(10)
    
    return role_arn

def create_lambda_zip(python_file):
    """Create a zip file for Lambda deployment"""
    zip_filename = f"{python_file.replace('.py', '')}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(python_file, arcname=python_file)
    
    with open(zip_filename, 'rb') as f:
        zip_content = f.read()
    
    os.remove(zip_filename)
    return zip_content

def create_lambda_function(function_name, python_file, role_arn):
    """Create or update a Lambda function"""
    print(f"📦 Creating/updating {function_name}...")
    
    zip_content = create_lambda_zip(python_file)
    handler = f"{python_file.replace('.py', '')}.lambda_handler"
    
    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': zip_content},
            Timeout=10,
            MemorySize=128,
            Description=f'Farm2Fork Cognito custom auth - {function_name}'
        )
        print(f"✅ {function_name} created")
        return response['FunctionArn']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print(f"⚠️  Function exists, updating code...")
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            print(f"✅ {function_name} updated")
            return response['FunctionArn']
        else:
            raise

def add_lambda_permission(function_name, account_id):
    """Add permission for Cognito to invoke Lambda"""
    source_arn = f"arn:aws:cognito-idp:{REGION}:{account_id}:userpool/{USER_POOL_ID}"
    
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='CognitoInvoke',
            Action='lambda:InvokeFunction',
            Principal='cognito-idp.amazonaws.com',
            SourceArn=source_arn
        )
        print(f"✅ Added Cognito invoke permission to {function_name}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceConflictException':
            print(f"⚠️  Permission already exists for {function_name}")
        else:
            print(f"⚠️  Error adding permission: {e}")

def configure_cognito_triggers(define_arn, create_arn, verify_arn):
    """Configure Cognito User Pool with Lambda triggers"""
    print_header("Step 3: Configuring Cognito User Pool triggers")
    
    try:
        cognito.update_user_pool(
            UserPoolId=USER_POOL_ID,
            LambdaConfig={
                'DefineAuthChallenge': define_arn,
                'CreateAuthChallenge': create_arn,
                'VerifyAuthChallengeResponse': verify_arn
            }
        )
        print("✅ Cognito User Pool triggers configured")
    except ClientError as e:
        print(f"❌ Error configuring triggers: {e}")
        raise

def enable_custom_auth():
    """Enable CUSTOM_AUTH flow in App Client"""
    print_header("Step 4: Enabling CUSTOM_AUTH flow in App Client")
    
    try:
        cognito.update_user_pool_client(
            UserPoolId=USER_POOL_ID,
            ClientId=APP_CLIENT_ID,
            ExplicitAuthFlows=['ALLOW_CUSTOM_AUTH', 'ALLOW_REFRESH_TOKEN_AUTH']
        )
        print("✅ App Client configured for custom auth")
    except ClientError as e:
        print(f"❌ Error configuring app client: {e}")
        raise

def main():
    """Main deployment function"""
    print_header("Cognito Lambda Deployment Script")
    print("Using Python/Boto3")
    
    try:
        # Get AWS account ID
        account_id = sts.get_caller_identity()['Account']
        print(f"✅ AWS Account ID: {account_id}")
        
        # Step 1: Create IAM role
        role_arn = create_iam_role()
        
        # Step 2: Create Lambda functions
        print_header("Step 2: Creating Lambda functions")
        
        define_arn = create_lambda_function(
            DEFINE_AUTH_FUNCTION,
            'define_auth_challenge.py',
            role_arn
        )
        
        create_arn = create_lambda_function(
            CREATE_AUTH_FUNCTION,
            'create_auth_challenge.py',
            role_arn
        )
        
        verify_arn = create_lambda_function(
            VERIFY_AUTH_FUNCTION,
            'verify_auth_challenge.py',
            role_arn
        )
        
        # Add permissions
        add_lambda_permission(DEFINE_AUTH_FUNCTION, account_id)
        add_lambda_permission(CREATE_AUTH_FUNCTION, account_id)
        add_lambda_permission(VERIFY_AUTH_FUNCTION, account_id)
        
        # Step 3: Configure Cognito
        configure_cognito_triggers(define_arn, create_arn, verify_arn)
        
        # Step 4: Enable custom auth
        enable_custom_auth()
        
        # Success message
        print_header("✅ Deployment Complete!")
        print("\nLambda Functions Created:")
        print(f"  - {DEFINE_AUTH_FUNCTION}")
        print(f"  - {CREATE_AUTH_FUNCTION}")
        print(f"  - {VERIFY_AUTH_FUNCTION}")
        print("\nNext Steps:")
        print("1. USE_COGNITO_AUTH is already set to true in backend/.env")
        print("2. Restart your backend server")
        print("3. Test with a real phone number (format: +919876543210)")
        print("\n⚠️  Note: SMS costs will apply for each OTP sent")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
