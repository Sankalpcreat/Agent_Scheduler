import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from agents.google_auth import authenticate_google_api


class TestGoogleAuth(unittest.TestCase):

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('google.oauth2.credentials.Credentials.from_authorized_user_info')
    def test_authenticate_with_existing_token(self, mock_from_user_info, mock_json_load, mock_open_file, mock_path_exists):
       
        mock_path_exists.return_value = True
        mock_json_load.return_value = {'token': 'test-token'}
        mock_creds = MagicMock(valid=True)
        mock_from_user_info.return_value = mock_creds

        creds = authenticate_google_api()

       
        mock_open_file.assert_called_with('token.json', 'r')
        mock_json_load.assert_called_once()
        mock_from_user_info.assert_called_once_with({'token': 'test-token'}, ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/tasks'])
        self.assertEqual(creds, mock_creds)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('google.auth.transport.requests.Request')
    @patch('google.oauth2.credentials.Credentials.from_authorized_user_info')
    def test_authenticate_with_expired_token(self, mock_from_user_info, mock_request, mock_open_file, mock_path_exists):
        
        mock_path_exists.return_value = True
        mock_creds = MagicMock(valid=False, expired=True, refresh_token='refresh_token')
        mock_from_user_info.return_value = mock_creds

        authenticate_google_api()

        
        mock_creds.refresh.assert_called_once_with(mock_request.return_value)

    @patch('os.path.exists')
    @patch('google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
    @patch('builtins.open', new_callable=mock_open)
    def test_authenticate_without_token(self, mock_open_file, mock_flow, mock_path_exists):
       
        mock_path_exists.side_effect = lambda x: x != 'token.json'

        mock_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance
        mock_creds = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_creds

        creds = authenticate_google_api()

        mock_flow.assert_called_once_with('credentials/credentials.json', ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/tasks'])
        mock_flow_instance.run_local_server.assert_called_once()
        mock_open_file.assert_called_with('token.json', 'w')
        self.assertEqual(creds, mock_creds)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
    def test_authenticate_with_missing_credentials_file(self, mock_flow, mock_open_file, mock_path_exists):
        
        mock_path_exists.side_effect = lambda x: x != 'credentials/credentials.json'

        with self.assertRaises(FileNotFoundError):
            authenticate_google_api()

       
        mock_flow.assert_not_called()


if __name__ == '__main__':
    unittest.main()