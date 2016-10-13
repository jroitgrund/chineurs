"""Tests for the flask controllers"""
from chineurs import facebook_authentication, main, group_feed, timestamp

from unittest.mock import Mock, patch

from flask import url_for
import pytest


@pytest.fixture
def flask_test_client():
    return main.APP.test_client()


@patch('chineurs.facebook_authentication.APP_ID', 'app_id')
@patch('chineurs.settings.REDIRECT_URI', 'redirect_uri')
def test_authenticate(flask_test_client):
    with main.APP.test_request_context():
        response = flask_test_client.get(url_for(
            'authenticate', group_id='group_id'))
        assert response.location == (
            'https://www.facebook.com/v2.8/dialog/oauth?'
            'client_id=app_id&redirect_uri='
            'redirect_uri/chine%3Fgroup_id%3Dgroup_id')


@patch('chineurs.settings.REDIRECT_URI', 'redirect_uri')
def test_chine(
        monkeypatch,
        flask_test_client):
    timestamp_mock = Mock()
    facebook_authentication_mock = Mock()
    group_feed_mock = Mock()
    timestamp_mock.return_value = 'last_timestamp'
    facebook_authentication_mock.return_value = 'access_token'
    group_feed_mock.return_value = ['foo']

    monkeypatch.setattr(
            timestamp, 'get_last_timestamp', timestamp_mock)
    monkeypatch.setattr(
            timestamp, 'write_last_timestamp', Mock())
    monkeypatch.setattr(
            facebook_authentication,
            'get_access_token',
            facebook_authentication_mock)
    monkeypatch.setattr(
            group_feed, 'get_youtube_links', group_feed_mock)

    with main.APP.test_request_context():
        response = flask_test_client.get(
                url_for('chine', group_id='group_id', code='code'))
        assert 'foo' in response.data.decode('utf-8')
    facebook_authentication_mock.assert_called_once_with(
            'code', 'redirect_uri/chine?group_id=group_id')
    group_feed_mock.assert_called_once_with(
            'group_id', 'access_token', 'last_timestamp')
