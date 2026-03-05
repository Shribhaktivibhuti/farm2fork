"""
Define Auth Challenge Lambda
This Lambda determines the authentication flow for custom auth
"""

def lambda_handler(event, context):
    """
    Determines which challenge to present to the user
    """
    print(f"Define Auth Challenge - Session: {event['request']['session']}")
    
    if len(event['request']['session']) == 0:
        # First attempt - send OTP challenge
        event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = False
        print("First attempt - issuing CUSTOM_CHALLENGE")
        
    elif len(event['request']['session']) == 1:
        # Second attempt - check if OTP was correct
        if event['request']['session'][0]['challengeName'] == 'CUSTOM_CHALLENGE':
            if event['request']['session'][0]['challengeResult']:
                # OTP was correct - issue tokens
                event['response']['issueTokens'] = True
                event['response']['failAuthentication'] = False
                print("OTP correct - issuing tokens")
            else:
                # OTP was wrong - give another chance
                event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
                event['response']['issueTokens'] = False
                event['response']['failAuthentication'] = False
                print("OTP incorrect - retry")
    
    elif len(event['request']['session']) >= 2:
        # Too many failed attempts
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = True
        print("Too many attempts - failing authentication")
    
    return event
