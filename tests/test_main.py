'''Tests for the flask controllers'''
from unittest.mock import patch

from flask import session

from chineurs import main
from chineurs.facebook_group import ExpiredFacebookToken


def setup_module(module):  # pylint: disable=W0613
    '''Set APP-wide config'''
    main.APP.secret_key = 'secret_key'
    main.APP.testing = True


@patch('chineurs.main.authentication', autospec=True)
def test_home(authentication):
    '''Home redirects to authenticate with no session cookie'''
    authentication.get_facebook_authentication_uri.return_value = 'fb_uri'
    with main.APP.test_client() as test_client:
        response = test_client.get('/')
        assert response.location == 'http://localhost/fb_uri'


def test_logout():
    '''Home erases session with ?new parameter'''
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['user_id'] = 'user_id'
        response = test_client.get('/logout')
        assert len(session) == 0
        assert response.location == 'http://localhost/'


@patch('chineurs.main.authentication', autospec=True)
@patch('chineurs.main.facebook_group', autospec=True)
# pylint:disable=unused-argument
def test_home_with_session(facebook_group, authentication):
    '''Home is served correctly with session cookie'''
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['user_id'] = 'user_id'
        response = test_client.get('/')
        assert 'Playlist' in response.data.decode('utf-8')
    facebook_group.save_groups.assert_called_once_with('user_id')
# pylint:enable=unused-argument


@patch('chineurs.main.authentication', autospec=True)
def test_facebook(authentication):
    '''Facebook endpoint gets FB token, redirects to Google OAuth'''
    authentication.get_google_authentication_uri.return_value = 'google_uri'

    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['user_id'] = 'user_id'
        response = test_client.get('/facebook?code=code')
        authentication.save_facebook_access_token.assert_called_once_with(
            'code', 'http://localhost/facebook')
        authentication.get_google_authentication_uri.assert_called_once_with(
            'http://localhost/google')
        assert response.location == 'http://localhost/google_uri'


@patch('chineurs.main.authentication', autospec=True)
def test_google(authentication):
    '''Google endpoint gets Google token, redirects to home'''
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['user_id'] = 'user_id'
        response = test_client.get('/google?code=code')
        authentication.save_google_credentials.assert_called_once_with(
            'user_id', 'code', 'http://localhost/google')
        assert response.location == ('http://localhost/')


@patch('chineurs.main.authentication', autospec=True)
@patch('chineurs.main.updates', autospec=True)
def test_update(updates, authentication):  # pylint:disable=unused-argument
    '''Update endpoint calls update with session and URL data'''
    updates.update.return_value = 'task_uuid'
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['user_id'] = 'user_id'
        response = test_client.get(
            '/update?group_id=group&playlist_id=playlist')
    updates.update.assert_called_once_with('user_id', 'group', 'playlist')
    assert response.data.decode('utf-8') == 'task_uuid'


@patch('chineurs.main.authentication', autospec=True)
@patch('chineurs.main.updates', autospec=True)
def test_update_raises(updates, authentication):
    '''If update raises an expired exception, main redirects'''
    def raise_expired(*args, **kwargs):  # pylint:disable=unused-argument
        '''Raises expired'''
        raise ExpiredFacebookToken()
    updates.update.side_effect = raise_expired
    authentication.get_facebook_authentication_uri.return_value = 'auth'
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['user_id'] = 'user_id'
        response = test_client.get(
            '/update?group_id=group&playlist_id=playlist')
        assert response.location == 'http://localhost/auth'


@patch('chineurs.main.storage', spec=True)
def test_done(storage):
    '''Test done endpoint'''
    storage.get_job_progress.return_value = 'progress'
    with main.APP.test_client() as test_client:
        response = test_client.get('/done/foo')
        assert '"progress": "progress"' in response.data.decode('utf-8')
    storage.get_job_progress.assert_called_once_with('foo')


@patch('chineurs.main.facebook_group', autospec=True)
def test_groups(facebook_group):
    '''Test search groups endpoint'''
    facebook_group.search_for_group.return_value = {'foo': 'bar'}
    with main.APP.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess['user_id'] = 'user_id'
        response = test_client.get('/groups/bar')
        assert response.data.decode('utf-8') == '{\n  "foo": "bar"\n}\n'
    facebook_group.search_for_group.assert_called_once_with(
        'user_id', 'bar')
