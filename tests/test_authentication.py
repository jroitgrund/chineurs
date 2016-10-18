'''Tests for authentication'''
from unittest.mock import Mock, patch

from chineurs import authentication


@patch('chineurs.authentication.Storage', autospec=True)
@patch('requests.get', autospec=True)
@patch('chineurs.settings.FACEBOOK_SECRET', 'FACEBOOK_SECRET')
def test_save_facebook_access_token(mock_requests_get, mock_storage):
    '''Tests that we get the token from the Facebook API'''
    mock_response = mock_requests_get.return_value()
    mock_requests_get.return_value = mock_response
    mock_response.json.return_value = {'access_token': 'access_token'}
    mock_storage_instance = Mock()
    mock_storage.return_value = mock_storage_instance

    authentication.save_facebook_access_token('uuid', 'code', 'redirect_uri')

    mock_storage.assert_called_once_with('uuid')
    mock_storage_instance.set.assert_called_once_with(
        'facebook-token', 'access_token')
    mock_requests_get.assert_called_once_with(
        'https://graph.facebook.com/v2.8/oauth/access_token?'
        'client_id={}&redirect_uri=redirect_uri&'
        'client_secret=FACEBOOK_SECRET&code=code'.format(
            authentication.FACEBOOK_APP_ID))
    mock_response.json.assert_called_once_with()


@patch('chineurs.authentication.Storage', autospec=True)
@patch('oauth2client.file.Storage', autospec=True)
def test_save_google_credentials_already_have(  # pylint:disable=invalid-name
        mock_google_storage, mock_storage):
    '''Tests that we read the token from file storage'''
    mock_storage_instance = Mock()
    mock_storage.return_value = mock_storage_instance
    mock_storage_instance.directory = '/data'

    mock_google_storage_instance = Mock()
    mock_google_storage.return_value = mock_google_storage_instance
    mock_google_storage_instance.get.return_value = 'foo'

    authentication.save_google_credentials('uuid', 'code', 'redirect_uri')

    mock_google_storage.assert_called_once_with('/data/google-credentials')
    mock_google_storage_instance.get.assert_called_once_with()


@patch('chineurs.authentication.Storage', autospec=True)
@patch('oauth2client.file.Storage', autospec=True)
@patch('chineurs.authentication.OAuth2WebServerFlow', autospec=True)
def test_save_google_credentials_get(  # pylint:disable=invalid-name
        mock_flow, mock_google_storage, mock_storage):
    '''Tests that we fetch the token from the API'''
    mock_flow_instance = Mock()
    mock_flow.return_value = mock_flow_instance
    mock_flow_instance.step2_exchange.return_value = 'token'

    mock_google_storage_instance = Mock()
    mock_google_storage.return_value = mock_google_storage_instance
    mock_google_storage_instance.get.return_value = None

    mock_storage_instance = Mock()
    mock_storage.return_value = mock_storage_instance
    mock_storage_instance.directory = 'data'

    authentication.save_google_credentials('uuid', 'code', 'redirect_uri')

    mock_google_storage.assert_called_once_with('data/google-credentials')
    mock_google_storage_instance.put.assert_called_once_with('token')
