'''Functions to interact with YouTube playlists'''
import requests


def insert_video(headers, playlist_id, video_id):
    '''Inserts a video in a playlist'''
    response = requests.post(
        'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet',
        headers=headers,
        json={
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        })
    return response
