'''Functions to interact with YouTube playlists'''
import itertools
import requests

from chineurs import authentication, pagination


def insert_video(headers, playlist_id, video_id):
    '''Inserts a video in a playlist'''
    response = requests.post(
        'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet',
        headers=headers,
        json={
            'snippet': {
                'playlistId': playlist_id,
                'position': 0,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        })
    return response


def get_playlists(headers):
    '''Gets all playlists'''
    url = (
        'https://www.googleapis.com/youtube/v3/playlists?'
        'part=snippet&mine=true')

    try:
        pages = list(pagination.get_paginated_resource(
            'https://www.googleapis.com/youtube/v3/playlists?'
            'part=snippet&mine=true',
            lambda page: (
                'nextPageToken' in page and
                '{}&pageToken={}'.format(url, page['nextPageToken'])),
            headers=headers))
    except requests.exceptions.HTTPError:
        raise authentication.AuthExpired()
    return sorted(
        [{'id': playlist['id'], 'name': playlist['snippet']['title']}
         for playlist in
         itertools.chain.from_iterable(page['items'] for page in pages)],
        key=lambda playlist: playlist['name'])
