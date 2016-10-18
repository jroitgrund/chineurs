'''Tests for the flask controllers'''
from unittest.mock import patch

from flask import session

from chineurs import facebook_group, main


def setup_module(module):  # pylint: disable=W0613
    '''Set APP-wide config'''
    main.APP.secret_key = 'secret_key'
    main.APP.testing = True


def test_home():
    '''Home redirects to authenticate with no session cookie'''
    with main.APP.test_client() as test_client:
        response = test_client.get('/')
        assert response.location == 'http://localhost/authenticate'


def test_logout():
    '''Home erases session with ?new parameter'''
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['uuid'] = 'uuid'
        response = test_client.get('/logout')
        assert len(session) == 0
        assert response.location == 'http://localhost/'


@patch('chineurs.main.authentication', autospec=True)
def test_home_with_session(authentication):
    '''Home is served correctly with session cookie'''
    authentication.get_facebook_access_token.return_value = 'foo'
    authentication.get_google_credentials.return_value = 'foo'
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['uuid'] = True
        response = test_client.get('/')
        assert 'Playlist' in response.data.decode('utf-8')


@patch('chineurs.main.authentication', autospec=True)
def test_authenticate(authentication):
    '''Authetication redirects to Facebook OAuth and sets session'''
    authentication.get_facebook_authentication_uri.return_value = 'fb_uri'
    with main.APP.test_client() as test_client:
        response = test_client.get('/authenticate')
        assert 'uuid' in session
        assert response.location == 'http://localhost/fb_uri'


def test_facebook_no_uuid():
    '''Facebook endpoint redirects to authenticate with no UUID'''

    with main.APP.test_client() as test_client:
        response = test_client.get('/facebook?code=code')
        assert response.location == 'http://localhost/authenticate'


@patch('chineurs.main.authentication', autospec=True)
def test_facebook(authentication):
    '''Facebook endpoint gets FB token, redirects to Google OAuth'''
    authentication.get_google_authentication_uri.return_value = 'google_uri'

    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['uuid'] = 'uuid'
        response = test_client.get('/facebook?code=code')
        authentication.save_facebook_access_token.assert_called_once_with(
            'uuid', 'code', 'http://localhost/facebook')
        authentication.get_google_authentication_uri.assert_called_once_with(
            'http://localhost/google')
        assert response.location == 'http://localhost/google_uri'


@patch('chineurs.main.authentication', autospec=True)
def test_google(authentication):
    '''Google endpoint gets Google token, redirects to home'''
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['uuid'] = 'uuid'
        response = test_client.get('/google?code=code')
        authentication.save_google_credentials.assert_called_once_with(
            'uuid', 'code', 'http://localhost/google')
        assert response.location == ('http://localhost/')


@patch('chineurs.main.authentication', autospec=True)
@patch('chineurs.main.updates', autospec=True)
def test_update(updates, authentication):
    '''Update endpoint calls update with session and URL data'''
    updates.update.return_value = 'data'
    authentication.get_facebook_access_token.return_value = 'foo'
    authentication.get_google_credentials.return_value = 'foo'
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['uuid'] = 'uuid'
        response = test_client.get(
            '/update?group_id=group&playlist_id=playlist')
    updates.update.assert_called_once_with('uuid', 'group', 'playlist')
    assert response.data.decode('utf-8') == '<br>'.join('data')


@patch('chineurs.main.authentication', autospec=True)
@patch('chineurs.main.updates', autospec=True)
def test_update_raises(updates, authentication):
    '''If update raises an expired exception, main redirects'''
    def raise_expired(*args, **kwargs):  # pylint:disable=unused-argument
        '''Raises expired'''
        raise facebook_group.ExpiredFacebookToken()
    updates.update.side_effect = raise_expired
    authentication.get_facebook_access_token.return_value = 'foo'
    authentication.get_google_credentials.return_value = 'foo'
    authentication.get_facebook_authentication_uri.return_value = 'auth'
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['uuid'] = 'uuid'
        response = test_client.get(
            '/update?group_id=group&playlist_id=playlist')
        assert response.location == 'http://localhost/auth'


@patch('chineurs.main.authentication', autospec=True)
def test_update_facebook_missing(authentication):
    '''Redirects if a facebook token is missing'''
    authentication.get_facebook_access_token.return_value = None
    authentication.get_facebook_authentication_uri.return_value = 'auth'
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['uuid'] = 'uuid'
        response = test_client.get(
            '/update?group_id=group&playlist_id=playlist')
        assert response.location == 'http://localhost/auth'


@patch('chineurs.main.authentication', autospec=True)
def test_update_google_missing(authentication):
    '''Redirects if a google token is missing'''
    authentication.get_facebook_access_token.return_value = 'token'
    authentication.get_google_credentials.return_value = None
    authentication.get_google_authentication_uri.return_value = 'auth'
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['uuid'] = 'uuid'
        response = test_client.get(
            '/update?group_id=group&playlist_id=playlist')
        assert response.location == 'http://localhost/auth'
