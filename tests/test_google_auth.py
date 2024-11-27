import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
from agents.google_auth import authenticate_google_api, SCOPES


class TestGoogleAuth(unittest.TestCase):
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
    def test_empty_token_file(self, mock_flow, mock_open_file, mock_path_exists):
        
        mock_path_exists.side_effect = lambda x: x in ['credentials/token.json', 'credentials/credentials.json']
        mock_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance
        mock_creds = MagicMock()
        mock_flow_instance.run_local_server.return_value = mock_creds

        creds = authenticate_google_api()

        mock_flow.assert_called_once_with(
            'credentials/credentials.json', SCOPES
        )
        mock_flow_instance.run_local_server.assert_called_once()
        mock_open_file.assert_called_with('credentials/token.json', 'w')
        self.assertEqual(creds, mock_creds)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"token": "test-token"}')
    @patch('json.load')
    @patch('google.oauth2.credentials.Credentials.from_authorized_user_info')
    def test_authenticate_with_existing_valid_token(
        self, mock_from_user_info, mock_json_load, mock_open_file, mock_path_exists
    ):
        
        mock_path_exists.return_value = True
        mock_json_load.return_value = {'token': 'test-token'}
        mock_creds = MagicMock(valid=True)
        mock_from_user_info.return_value = mock_creds

        creds = authenticate_google_api()

        mock_open_file.assert_called_with('credentials/token.json', 'r')
        mock_json_load.assert_called_once()
        mock_from_user_info.assert_called_once_with(
            {'token': 'test-token'}, SCOPES
        )
        self.assertEqual(creds, mock_creds)

 


if __name__ == '__main__':
    unittest.main()