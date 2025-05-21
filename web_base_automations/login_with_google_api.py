import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from generate_token_file import authenticate_gmail_api
from utils import *

def get_last_email_from_sender(service, sender_email,logger):
    """Get the last email from a specific sender."""
    try:
        # List messages from the sender
        query = f'from:{sender_email}'
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            print(f'No messages found from {sender_email}.')
            logger.info(f'No messages found from {sender_email}.')
            return None
        
        # Get the most recent message
        message_id = messages[0]['id']
        message = service.users().messages().get(userId='me', id=message_id).execute()

        # Get the email content
        snippet = message['snippet']
        print(f'Last email from {sender_email}:')
        print("message : ",snippet)
        logger.info(f'fethched message: {snippet}')
        return snippet

    except HttpError as error:
        print(f'An error occurred: {error}')
        logger.info(f'An error occurred: {error}')
        return None
    

def extract_otp(snippet):
    """Extract the OTP from the email snippet using regex."""
    # Regex pattern for a 6-digit number
    otp_pattern = r'\b\d{6}\b'
    match = re.search(otp_pattern, snippet)
    if match:
        return match.group(0)
    return None

def otp_get_from(logger):
    service = authenticate_gmail_api()
    print("service : ", service)
    sender_email = 'noreply@no-reply.konnectd.io'
    last_email = get_last_email_from_sender(service, sender_email,logger)
    print("last_email : ", last_email)
    otp =  extract_otp(last_email)
    print("otp : ", otp)
    if last_email:
        logger.info('Otp fetch sucessfully')
        print('Otp fetch sucessfully')
        return otp
    else:
        print('Otp not fetch sucessfully')
        logger.info('Otp not fetch sucessfully')
        return 000000


 