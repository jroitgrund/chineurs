'''Tests for facebook_group'''
from unittest.mock import call, Mock, patch

import pytest

from chineurs import facebook_group


@pytest.fixture
def requests_get_mock():
    '''Sets up a mock requests.get method with two pages of a Faceook
       group feed API results'''
    page1 = Mock()
    page2 = Mock()
    page1.json.return_value = {
        'data': [
            {
                'message': 'woo! youtube.com/bar is sick',
                'updated_time': '2016-01-01T00:00:00+0000'
            },
            {
                'message': 'woo! youtube.com/baz is sick',
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
                'message': 'woo! youtube.com/bam is sick',
                'updated_time': '2016-01-01T00:00:00+0000'
            },
            {
                'message': 'woo! youtube.com/bak is sick',
                'updated_time': '2016-01-01T00:00:00+0000'
            },
            {
                'message': 'no link here :(',
                'updated_time': '2016-01-01T00:00:00+0000'
            }
        ]
    }

    requests_get_mock = Mock()
    requests_get_mock.side_effect = [page1, page2]
    return requests_get_mock


def test_get_youtube_links(requests_get_mock):
    '''Tests that we get YouTube links from the Facebook API'''
    with patch('requests.get', requests_get_mock):
        links = facebook_group.get_youtube_links(
            'group_id', 'access_token', '0001-01-01T00:00:00+0000')

        requests_get_mock.assert_has_calls([
            call(
                'https://graph.facebook.com/v2.8/group_id/feed?'
                'access_token=access_token'),
            call('next')])
        assert links == [
                'youtube.com/bar',
                'youtube.com/baz',
                'youtube.com/bam',
                'youtube.com/bak']


def test_get_links_timestamp(requests_get_mock):
    '''Tests that we get YouTube links from the Facebook API and filter out
       old ones'''
    with patch('requests.get', requests_get_mock):
        links = facebook_group.get_youtube_links(
            'group_id', 'access_token', '2015-01-01T00:00:00+0000')

        requests_get_mock.assert_called_once_with(
            'https://graph.facebook.com/v2.8/group_id/feed?'
            'access_token=access_token')
        assert links == ['youtube.com/bar']
