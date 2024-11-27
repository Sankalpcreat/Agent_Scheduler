from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import json
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks',
]

def authenticate_google_api():
    creds = None
    token_path = 'credentials/token.json'
    credentials_path = 'credentials/credentials.json'

    if os.path.exists(token_path):
        try:
            with open(token_path, 'r') as token_file:
                token_data = json.load(token_file)
                creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except (json.JSONDecodeError, ValueError):
            print("Invalid or empty token.json. Proceeding with OAuth flow.")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError("The credentials.json file is missing.")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds