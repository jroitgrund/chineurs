'''Tests for authentication'''
from unittest.mock import patch

from chineurs import authentication


@patch('chineurs.authentication.storage', spec=True)
@patch('requests.get', autospec=True)
@patch('chineurs.settings.FACEBOOK_SECRET', 'FACEBOOK_SECRET')
def test_save_facebook_access_token(mock_requests_get, mock_storage):
    '''Tests that we get the token from the Facebook API'''
    mock_requests_get.return_value.json.side_effect = [
        {'access_token': 'access_token'},
        {'id': 'user_id'}]
    mock_storage.get_user_id.return_value = 'id'

    assert authentication.save_facebook_access_token(
        'code', 'redirect_uri') == 'id'

    mock_storage.get_user_id.assert_called_once_with(
        'user_id', 'access_token')


@patch('chineurs.authentication.storage', spec=True)
def test_save_google_credentials_already_have(  # pylint:disable=invalid-name
        mock_storage):
    '''Tests that we read the token from file storage'''
    mock_storage.get_user_by_id.return_value = {'google_credentials': 'foo'}

    authentication.save_google_credentials('user_id', 'code', 'redirect_uri')

    mock_storage.set_user_google_credentials.assert_has_calls([])


@patch('chineurs.authentication.storage', spec=True)
@patch('chineurs.authentication.OAuth2WebServerFlow', autospec=True)
def test_save_google_credentials_get(  # pylint:disable=invalid-name
        mock_flow, mock_storage):
    '''Tests that we fetch the token from the API'''
    mock_flow.return_value.step2_exchange.return_value = 'token'
    mock_storage.get_user_by_id.return_value = {}

    authentication.save_google_credentials('user_id', 'code', 'redirect_uri')

    mock_storage.set_user_google_credentials.assert_called_once_with(
        'user_id', 'token')
