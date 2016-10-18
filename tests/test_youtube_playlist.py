'''Tests for youtube playlist'''
from asyncio import Future
from unittest.mock import Mock, patch

from chineurs import youtube_playlist


@patch('chineurs.youtube_playlist.AsyncHTTPClient', autospec=True)
# pylint:disable=unused-argument
def test_insert_videos(asynchttpclient):
    '''Make HTTP calls to the youtube API'''
    results = [Future() for x in range(10)]
    for result in results:
        result.set_result(Mock())

    asynchttpclient.return_value.fetch.side_effect = results

    assert len(youtube_playlist.insert_videos(
        Mock(), 'playlist', range(10))) == 10
