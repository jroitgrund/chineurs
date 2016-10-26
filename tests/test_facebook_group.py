'''Tests for facebook_group'''
import asyncio
from collections import OrderedDict
from datetime import datetime
import json
from unittest.mock import call, Mock, patch

import pytest
import pytz
import requests

from chineurs import authentication, facebook_group, timestamp


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
                'updated_time': '2016-01-01T00:00:00+0000',
                'id': 1,
            },
            {
                'message': 'no link here :(',
                'updated_time': '2016-01-01T00:00:00+0000',
                'id': 2,
            },
            {
                'message': '',
                'link': 'youtube.com/watch?v=baz',
                'updated_time': '2013-01-01T00:00:00+0000',
                'id': 3,
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
                'updated_time': '2016-01-01T00:00:00+0000',
                'id': 4,
            },
            {
                'updated_time': '2016-01-01T00:00:00+0000',
                'id': 5,
            },
            {
                'message': 'no link here :(',
                'updated_time': '2016-01-01T00:00:00+0000',
                'id': 6,
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
    assert links == OrderedDict([
        (1, ['bar']),
        (2, []),
        (3, ['baz']),
        (4, ['bam', 'bak']),
        (5, []),
        (6, []),
    ])


# pylint: disable=C0103
@patch('chineurs.facebook_group.AsyncHTTPClient', autospec=True)
def test_get_youtube_links_from_comments(http_client):
    '''Tests that we asynchronously fetch links in a post's comments'''
    # pylint:disable=W0613,C0111
    async def async_get(url, raise_error=False):
        response = Mock()
        Mock.body = json.dumps({
            'data': [
                {'message': 'youtube.com/watch?v=baz'},
                {'message': 'youtube.com/watch?v=bar'},
            ]
        }).encode('utf-8')
        return response
    http_client.return_value.fetch.side_effect = async_get
    # pylint:enable=W0613,C0111

    assert list(asyncio.get_event_loop().run_until_complete(
        facebook_group.get_youtube_links_from_comments('post_id', 'f'))) == [
            'baz', 'bar']

    http_client.return_value.fetch.assert_called_once_with(
        'https://graph.facebook.com/v2.8/post_id/comments?'
        'filter=stream&access_token=f', raise_error=False)


# pylint: disable=invalid-name
def test_get_youtube_links_expired_token(requests_get, monkeypatch):
    '''Tests that when the token is expired an exception is raised'''
    monkeypatch.setattr('requests.get', requests_get)

    def raise_expired(*args, **kwargs):  # pylint:disable=unused-argument
        '''Raises expired'''
        raise requests.exceptions.HTTPError
    requests_get.side_effect = raise_expired
    with pytest.raises(authentication.AuthExpired):
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
    assert links == OrderedDict([
        (1, ['bar']),
        (2, []),
    ])


@patch('chineurs.facebook_group.requests.get', autospec=True)
def test_get_facebook_id(requests_get):
    '''Test get_facebook_id'''
    requests_get.return_value.json.return_value = {'id': 'myid'}

    assert facebook_group.get_facebook_id('token') == 'myid'


@patch('chineurs.facebook_group.requests.get', autospec=True)
def test_get_groups(requests_get):
    '''Test get groups'''
    groups = [
        {'name': 'name1', 'id': 'id1'},
        {'name': 'name2', 'id': 'id2'},
    ]
    requests_get.return_value.json.return_value = {
        'data': groups
    }

    assert facebook_group.get_groups('access_token') == groups

    requests_get.assert_called_once_with(
        'https://graph.facebook.com/v2.8/me/groups?'
        'limit=1000&access_token=access_token')
