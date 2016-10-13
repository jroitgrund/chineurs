'''Tests for the flask controllers'''
from unittest.mock import patch

from flask import session

from chineurs import authentication, main


def setup_module(module):
    main.APP.secret_key = 'secret_key'
    main.APP.testing = True


def test_home():
    with main.APP.test_client() as test_client:
        response = test_client.get('/')
        assert response.location == 'http://localhost/authenticate'


def test_home_new():
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['facebook_access_token'] = True
            sess['google_access_token'] = True
        response = test_client.get('/?new=True')
        assert len(session) == 0
        assert response.location == 'http://localhost/authenticate'


def test_home_with_session():
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['facebook_access_token'] = True
            sess['google_access_token'] = True
        response = test_client.get('/')
        assert 'Playlist' in response.data.decode('utf-8')


def test_authenticate():
    with main.APP.test_client() as test_client:
        response = test_client.get('/authenticate')
        assert response.location == (
            'https://www.facebook.com/v2.8/dialog/oauth?'
            'client_id={}&redirect_uri={}').format(
                authentication.FACEBOOK_APP_ID,
                'http%3A//localhost/facebook')


@patch('chineurs.authentication.get_facebook_access_token', autospec=True)
def test_facebook(get_facebook_access_token_mock):
    get_facebook_access_token_mock.return_value = 'access_token'

    with main.APP.test_client() as test_client:
        response = test_client.get('/facebook?code=code')
        get_facebook_access_token_mock.assert_called_once_with(
                'code', 'http%3A//localhost/facebook')

        assert session['facebook_access_token'] == 'access_token'
        assert response.location == (
            'https://accounts.google.com/o/oauth2/v2/auth?'
            'scope=https://www.googleapis.com/auth/youtube&'
            'response_type=code&'
            'client_id={}&redirect_uri={}'.format(
                authentication.GOOGLE_APP_ID, 'http%3A//localhost/google'))


@patch('chineurs.authentication.get_google_access_token', autospec=True)
def test_google(get_google_access_token_mock):
    get_google_access_token_mock.return_value = 'access_token'

    with main.APP.test_client() as test_client:
        response = test_client.get('/google?code=code')
        get_google_access_token_mock.assert_called_once_with(
                'code', 'http%3A//localhost/google')

        assert session['google_access_token'] == 'access_token'
        assert response.location == ('http://localhost/')


@patch('chineurs.updates.update', autospec=True)
def test_update(update):
    update.return_value = 'data'
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['facebook_access_token'] = 'fb'
            sess['google_access_token'] = 'g'
        response = test_client.post('update', data={
            'groupId': 'group',
            'playlistId': 'playlist'
        })
    update.assert_called_once_with('fb', 'group', 'g', 'playlist')
    assert response.data.decode('utf-8') == 'data'
