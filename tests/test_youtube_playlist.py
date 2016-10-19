'''Tests for youtube playlist'''
from unittest.mock import patch

from chineurs import youtube_playlist


@patch('chineurs.youtube_playlist.requests', autospec=True)
def test_insert_videos(requests):
    '''Make HTTP calls to the youtube API'''
    requests.post.return_value = 5

    assert youtube_playlist.insert_video({}, 'playlist', 'vid') == 5

    requests.post.assert_called_once_with(
        'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet',
        headers={},
        json={
            'snippet': {
                'playlistId': 'playlist',
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': 'vid'
                }
            }
        })
