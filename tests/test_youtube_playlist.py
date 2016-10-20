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
                'position': 0,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': 'vid'
                }
            }
        })


@patch('chineurs.youtube_playlist.requests.get', autospec=True)
def test_get_playlists(requests_get):
    '''Get playlists from YouTube api'''
    requests_get.return_value.json.return_value = {
        'items': [
            {
                'id': 'id1',
                'snippet': {
                    'title': 'name1'
                }
            },
            {
                'id': 'id2',
                'snippet': {
                    'title': 'name2'
                }
            }
        ]
    }

    assert youtube_playlist.get_playlists({}) == [
        {
            'id': 'id1',
            'name': 'name1'
        },
        {
            'id': 'id2',
            'name': 'name2'
        }
    ]
