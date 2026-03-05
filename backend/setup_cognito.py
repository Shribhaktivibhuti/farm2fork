"""
AWS Cognito Setup Helper Script

This script helps verify Cognito configuration and test connectivity.
Run this before enabling Cognito authentication in production.
"""

import os
import sys
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("=" * 60)
    print("Checking Environment Variables")
    print("=" * 60)
    
    required_vars = [
        'AWS_REGION',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'COGNITO_USER_POOL_ID',
        'COGNITO_CLIENT_ID'
    ]
    
    optional_vars = [
        'COGNITO_CLIENT_SECRET',
        'USE_COGNITO_AUTH'
    ]
    
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                display_value = value[:8] + '...' if len(value) > 8 else '***'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_set = False
    
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var:
                display_value = value[:8] + '...' if len(value) > 8 else '***'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚠️  {var}: NOT SET (optional)")
    
    return all_set


def test_aws_credentials():
    """Test AWS credentials"""
    print("\n" + "=" * 60)
    print("Testing AWS Credentials")
    print("=" * 60)
    
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS credentials valid")
        print(f"   Account: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        return True
        
    except Exception as e:
        print(f"❌ AWS credentials invalid: {str(e)}")
        return False


def test_cognito_connection():
    """Test connection to Cognito User Pool"""
    print("\n" + "=" * 60)
    print("Testing Cognito Connection")
    print("=" * 60)
    
    try:
        user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
        region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not user_pool_id:
            print("❌ COGNITO_USER_POOL_ID not set")
            return False
        
        client = boto3.client('cognito-idp', region_name=region)
        
        # Describe user pool
        response = client.describe_user_pool(UserPoolId=user_pool_id)
        
        pool = response['UserPool']
        print(f"✅ Connected to Cognito User Pool")
        print(f"   Pool Name: {pool['Name']}")
        print(f"   Pool ID: {pool['Id']}")
        print(f"   Status: {pool['Status']}")
        print(f"   Creation Date: {pool['CreationDate']}")
        
        # Check SMS configuration
        if 'SmsConfiguration' in pool:
            print(f"   SMS Configured: ✅")
        else:
            print(f"   SMS Configured: ⚠️  Not configured")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Cognito connection failed: {error_code}")
        print(f"   {error_message}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def test_app_client():
    """Test Cognito App Client configuration"""
    print("\n" + "=" * 60)
    print("Testing Cognito App Client")
    print("=" * 60)
    
    try:
        user_pool_id = os.getenv('COGNITO_USER_POOL_ID')
        client_id = os.getenv('COGNITO_CLIENT_ID')
        region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not client_id:
            print("❌ COGNITO_CLIENT_ID not set")
            return False
        
        client = boto3.client('cognito-idp', region_name=region)
        
        # Describe app client
        response = client.describe_user_pool_client(
            UserPoolId=user_pool_id,
            ClientId=client_id
        )
        
        app_client = response['UserPoolClient']
        print(f"✅ App Client found")
        print(f"   Client Name: {app_client['ClientName']}")
        print(f"   Client ID: {app_client['ClientId']}")
        
        # Check auth flows
        auth_flows = app_client.get('ExplicitAuthFlows', [])
        print(f"   Auth Flows: {', '.join(auth_flows)}")
        
        if 'ALLOW_CUSTOM_AUTH' in auth_flows:
            print(f"   Custom Auth: ✅ Enabled")
        else:
            print(f"   Custom Auth: ❌ Not enabled (required for OTP)")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ App client check failed: {error_code}")
        print(f"   {error_message}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def test_sns_permissions():
    """Test SNS permissions for SMS"""
    print("\n" + "=" * 60)
    print("Testing SNS SMS Permissions")
    print("=" * 60)
    
    try:
        region = os.getenv('AWS_REGION', 'us-east-1')
        sns = boto3.client('sns', region_name=region)
        
        # Get SMS attributes
        response = sns.get_sms_attributes()
        
        attributes = response.get('attributes', {})
        
        print(f"✅ SNS accessible")
        
        if 'DefaultSMSType' in attributes:
            print(f"   SMS Type: {attributes['DefaultSMSType']}")
        
        if 'MonthlySpendLimit' in attributes:
            print(f"   Monthly Spend Limit: ${attributes['MonthlySpendLimit']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"⚠️  SNS check failed: {error_code}")
        print(f"   This is optional if Cognito handles SMS directly")
        return True  # Not critical
    except Exception as e:
        print(f"⚠️  SNS check error: {str(e)}")
        return True  # Not critical


def print_next_steps():
    """Print next steps for setup"""
    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    
    use_cognito = os.getenv('USE_COGNITO_AUTH', 'false').lower() == 'true'
    
    if use_cognito:
        print("✅ Cognito authentication is ENABLED")
        print("\nTo test:")
        print("1. Start the backend: uvicorn main:app --reload")
        print("2. Test OTP request:")
        print('   curl -X POST http://localhost:8000/api/auth/request-otp \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"phone_number": "+919876543210"}\'')
        print("\n3. Check your phone for SMS OTP")
        print("4. Verify OTP:")
        print('   curl -X POST http://localhost:8000/api/auth/verify-otp \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"phone_number": "+919876543210", "otp": "123456", "name": "Test"}\'')
    else:
        print("ℹ️  Cognito authentication is DISABLED (Demo mode)")
        print("\nTo enable Cognito:")
        print("1. Set USE_COGNITO_AUTH=true in .env")
        print("2. Configure all Cognito environment variables")
        print("3. Run this script again to verify")
        print("\nTo test demo mode:")
        print("1. Use OTP: 0000")
        print("2. Any phone number will work")


def main():
    """Main setup verification"""
    print("\n" + "=" * 60)
    print("AWS COGNITO SETUP VERIFICATION")
    print("=" * 60)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n❌ Missing required environment variables")
        print("Please set all required variables in .env file")
        sys.exit(1)
    
    # Test AWS credentials
    aws_ok = test_aws_credentials()
    
    if not aws_ok:
        print("\n❌ AWS credentials test failed")
        sys.exit(1)
    
    # Test Cognito connection
    cognito_ok = test_cognito_connection()
    
    # Test app client
    client_ok = test_app_client()
    
    # Test SNS (optional)
    test_sns_permissions()
    
    # Print summary
    print("\n" + "=" * 60)
    print("SETUP VERIFICATION SUMMARY")
    print("=" * 60)
    
    if env_ok and aws_ok and cognito_ok and client_ok:
        print("✅ All checks passed!")
        print("✅ Cognito is ready to use")
    else:
        print("⚠️  Some checks failed")
        print("Please review the errors above")
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
