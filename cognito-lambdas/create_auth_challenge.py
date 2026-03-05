"""
Create Auth Challenge Lambda
This Lambda generates the OTP code and sends it via SMS
"""

import random
import boto3
import os

def lambda_handler(event, context):
    """
    Generates OTP and stores it in the session
    Cognito will automatically send SMS if SMS configuration is set up
    """
    print(f"Create Auth Challenge - Challenge Name: {event['request']['challengeName']}")
    
    if event['request']['challengeName'] == 'CUSTOM_CHALLENGE':
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        print(f"Generated OTP: {otp}")
        
        # Store OTP in private challenge parameters (not visible to client)
        event['response']['privateChallengeParameters'] = {
            'otp': otp
        }
        
        # Public challenge parameters (visible to client)
        event['response']['publicChallengeParameters'] = {
            'phone': event['request']['userAttributes'].get('phone_number', 'unknown')
        }
        
        # Challenge metadata
        event['response']['challengeMetadata'] = 'OTP_CHALLENGE'
        
        # Send SMS via SNS (optional - Cognito can handle this automatically)
        try:
            phone_number = event['request']['userAttributes'].get('phone_number')
            if phone_number:
                sns = boto3.client('sns')
                message = f'Your Farm2Fork verification code is: {otp}. Valid for 5 minutes.'
                
                sns.publish(
                    PhoneNumber=phone_number,
                    Message=message,
                    MessageAttributes={
                        'AWS.SNS.SMS.SMSType': {
                            'DataType': 'String',
                            'StringValue': 'Transactional'
                        }
                    }
                )
                print(f"SMS sent to {phone_number}")
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            # Continue anyway - Cognito might handle SMS
    
    return event
