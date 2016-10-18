'''Tests for youtube playlist'''
from unittest.mock import Mock, patch

from chineurs import youtube_playlist


@patch('chineurs.youtube_playlist.requests', autospec=True)
# pylint:disable=unused-argument
def test_insert_videos(requests):
    '''Make HTTP calls to the youtube API'''
    requests.post.return_value.json = 5

    assert len(youtube_playlist.insert_videos(
        Mock(), 'playlist', range(10))) == 10
