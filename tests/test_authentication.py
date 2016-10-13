'''Tests for authentication'''
from unittest.mock import patch

from chineurs import authentication


@patch('requests.get', autospec=True)
@patch('chineurs.settings.FACEBOOK_SECRET', 'FACEBOOK_SECRET')
def test_get_facebook_access_token(mock_requests_get):
    '''Tests that we get the token from the Facebook API'''
    mock_response = mock_requests_get.return_value()
    mock_requests_get.return_value = mock_response
    mock_response.json.return_value = {'access_token': 'access_token'}

    access_token = authentication.get_facebook_access_token(
        'code', 'redirect_uri')

    mock_requests_get.assert_called_once_with(
        'https://graph.facebook.com/v2.8/oauth/access_token?'
        'client_id={}&redirect_uri=redirect_uri&'
        'client_secret=FACEBOOK_SECRET&code=code'.format(
            authentication.FACEBOOK_APP_ID))
    mock_response.json.assert_called_once_with()
    assert access_token == 'access_token'


@patch('requests.post', autospec=True)
@patch('chineurs.settings.GOOGLE_SECRET', 'GOOGLE_SECRET')
def test_get_google_access_token(mock_requests_post):
    '''Tests that we get the token from the Facebook API'''
    mock_response = mock_requests_post.return_value()
    mock_requests_post.return_value = mock_response
    mock_response.json.return_value = {'access_token': 'access_token'}

    access_token = authentication.get_google_access_token(
        'code', 'redirect_uri')

    mock_requests_post.assert_called_once_with(
        'https://www.googleapis.com/oauth2/v4/token',
        data={
            'grant_type': 'authorization_code',
            'client_id': authentication.GOOGLE_APP_ID,
            'redirect_uri': 'redirect_uri',
            'client_secret': 'GOOGLE_SECRET',
            'code': 'code'
        })
    mock_response.json.assert_called_once_with()
    assert access_token == 'access_token'
