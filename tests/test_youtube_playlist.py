'''Tests for youtube playlist'''
from unittest.mock import Mock, patch

from chineurs import youtube_playlist


@patch('chineurs.youtube_playlist.AsyncHTTPClient', autospec=True)
# pylint:disable=unused-argument
def test_insert_videos(asynchttpclient):
    '''Make HTTP calls to the youtube API'''
    youtube_playlist.insert_videos(Mock(), 'playlist', range(10))
    assert len(asynchttpclient.return_value.fetch.call_args_list) == 10
