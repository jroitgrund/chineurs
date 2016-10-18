'''Functions to interact with YouTube playlists'''
import requests


def insert_videos(credentials, playlist_id, video_ids):
    '''Inserts videos in a playlist asynchronously'''
    return [insert_video(credentials, playlist_id, video_id)
            for video_id in video_ids]


def insert_video(credentials, playlist_id, video_id):
    '''Inserts a video in a playlist'''
    headers = {}
    credentials.apply(headers)
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
