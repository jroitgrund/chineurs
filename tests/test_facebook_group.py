'''Tests for facebook_group'''
from unittest.mock import call, Mock

import pytest
import requests

from chineurs import facebook_group


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
        'group_id', 'access_token', '0001-01-01T00:00:00+0000')

    requests_get.assert_has_calls([
        call(
            'https://graph.facebook.com/v2.8/group_id/feed?'
            'access_token=access_token&fields=id,message,link,updated_time&'
            'limit=1000'),
        call('next')])
    assert list(links) == [
        'bar',
        'baz',
        'bam',
        'bak']


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
            'group_id', 'access_token', '0001-01-01T00:00:00+0000')


# pylint: disable=W0621
def test_get_youtube_links_filter_timestamp(requests_get, monkeypatch):
    '''Tests that we get YouTube links from the Facebook API and filter out
       old ones'''
    monkeypatch.setattr('requests.get', requests_get)
    links = facebook_group.get_youtube_links(
        'group_id', 'access_token', '2015-01-01T00:00:00+0000')

    requests_get.assert_called_once_with(
        'https://graph.facebook.com/v2.8/group_id/feed?'
        'access_token=access_token&fields=id,message,link,updated_time&'
        'limit=1000')
    assert list(links) == ['bar']
