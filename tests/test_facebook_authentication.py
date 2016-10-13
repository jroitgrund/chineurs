"""Tests for facebook_authentication"""
from unittest.mock import patch

from chineurs import facebook_authentication


@patch('requests.get', autospec=True)
@patch('chineurs.settings.APP_SECRET', 'APP_SECRET')
def test_get_access_token(mock_requests_get):
    """Tests that we get the token from the Facebook API"""
    mock_response = mock_requests_get.return_value()
    mock_requests_get.return_value = mock_response
    mock_response.json.return_value = {'access_token': 'access_token'}

    access_token = facebook_authentication.get_access_token(
        'code', 'redirect_uri')

    mock_requests_get.assert_called_once_with(
        'https://graph.facebook.com/v2.8/oauth/access_token?'
        'client_id=%s&redirect_uri=redirect_uri&'
        'client_secret=APP_SECRET&code=code' %
        facebook_authentication.APP_ID)
    mock_response.json.assert_called_once_with()
    assert access_token == 'access_token'
