'''Tests for facebook_group'''
from datetime import datetime
from unittest.mock import call, Mock, patch

import pytest
import pytz
import requests

from chineurs import facebook_group, timestamp


@pytest.fixture
def requests_get():
    '''Sets up a mock requests.get method with two pages of a Faceook
       group feed API results'''
    page1 = Mock()
    page2 = Mock()
    page1.json.return_value = {
        'data': [
            {
                'message': 'woo! youtube.com/watch?v=bar is sick',
                'updated_time': '2016-01-01T00:00:00+0000'
            },
            {
                'message': '',
                'link': 'youtube.com/watch?v=baz',
                'updated_time': '2013-01-01T00:00:00+0000'
            },
            {
                'message': 'no link here :(',
                'updated_time': '2016-01-01T00:00:00+0000'
            }
        ],
        'paging': {
            'next': 'next'
        }
    }
    page2.json.return_value = {
        'data': [
            {
                'message': 'woo! youtube.com/watch?v=bam is sick',
                'link': 'youtube.com/watch?v=bak',
                'updated_time': '2016-01-01T00:00:00+0000'
            },
            {
                'updated_time': '2016-01-01T00:00:00+0000'
            },
            {
                'message': 'no link here :(',
                'updated_time': '2016-01-01T00:00:00+0000'
            }
        ]
    }

    mock = Mock()
    mock.side_effect = [page1, page2]
    return mock


# pylint: disable=W0621
def test_get_youtube_links(requests_get, monkeypatch):
    '''Tests that we get YouTube links from the Facebook API'''
    monkeypatch.setattr('requests.get', requests_get)
    links = facebook_group.get_youtube_links(
        'group_id', 'access_token', timestamp.DEFAULT_DATETIME)

    requests_get.assert_has_calls([
        call(
            'https://graph.facebook.com/v2.8/group_id/feed?'
            'access_token=access_token&fields=id,message,link,updated_time&'
            'limit=1000'),
        call('next')])
    assert list(links) == [
        'bak',
        'bam',
        'baz',
        'bar']


# pylint: disable=invalid-name
def test_get_youtube_links_expired_token(requests_get, monkeypatch):
    '''Tests that when the token is expired an exception is raised'''
    monkeypatch.setattr('requests.get', requests_get)

    def raise_expired(*args, **kwargs):  # pylint:disable=unused-argument
        '''Raises expired'''
        raise requests.exceptions.HTTPError
    requests_get.side_effect = raise_expired
    with pytest.raises(facebook_group.ExpiredFacebookToken):
        facebook_group.get_youtube_links(
            'group_id', 'access_token', timestamp.DEFAULT_DATETIME)


# pylint: disable=W0621
def test_get_youtube_links_filter_timestamp(requests_get, monkeypatch):
    '''Tests that we get YouTube links from the Facebook API and filter out
       old ones'''
    monkeypatch.setattr('requests.get', requests_get)
    links = facebook_group.get_youtube_links(
        'group_id', 'access_token', datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc))

    requests_get.assert_called_once_with(
        'https://graph.facebook.com/v2.8/group_id/feed?'
        'access_token=access_token&fields=id,message,link,updated_time&'
        'limit=1000')
    assert list(links) == ['bar']


@patch('chineurs.facebook_group.requests.get', autospec=True)
def test_get_facebook_id(requests_get):
    '''Test get_facebook_id'''
    requests_get.return_value.json.return_value = {'id': 'myid'}

    assert facebook_group.get_facebook_id('token') == 'myid'


@patch('chineurs.facebook_group.storage', spec=True)
@patch('chineurs.facebook_group.requests.get', autospec=True)
def test_save_groups(requests_get, storage):
    '''Test save groups'''
    groups = [
        {'name': 'name1', 'id': 'id1'},
        {'name': 'name2', 'id': 'id2'},
    ]
    requests_get.return_value.json.return_value = {
        'data': groups
    }
    storage.get_user_by_id.return_value = {'fb_access_token': 'access_token'}

    facebook_group.save_groups('user_id')

    requests_get.assert_called_once_with(
        'https://graph.facebook.com/v2.8/me/groups?'
        'limit=1000&access_token=access_token')
    storage.save_facebook_groups.assert_called_once_with('user_id', groups)


@patch('chineurs.facebook_group.storage', spec=True)
def test_search_for_group(storage):
    '''Test search for group'''
    groups = [
        {'name': 'name1', 'id': 'id1'},
        {'name': 'name2', 'id': 'id2'},
    ]
    storage.get_facebook_groups.return_value = groups + [
        {'name': 'baz', 'id': 'bar'}]

    assert facebook_group.search_for_group('user_id', 'name') == groups

    storage.get_facebook_groups.assert_called_once_with('user_id')
