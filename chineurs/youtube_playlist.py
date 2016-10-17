'''Functions to interact with YouTube playlists'''
import json

from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop

from chineurs.app import APP


def log_error(response):
    '''Log an error response'''
    APP.logger.error(response.reason, exc_info=response.error)


def insert_videos(credentials, playlist_id, video_ids):
    '''Inserts videos in a playlist asynchronously'''
    shared_state = {'requests_remaining': len(video_ids)}
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()
    responses = [
        insert_video(credentials, playlist_id, video_id, io_loop, shared_state)
        .result()
        for video_id in video_ids]
    map(
        log_error,
        [response for response in responses if response.error])
    return responses


def insert_video(credentials, playlist_id, video_id, io_loop, shared_state):
    '''Inserts a video in a playlist'''
    http_client = AsyncHTTPClient()
    headers = {}
    credentials.apply(headers)
    response = http_client.fetch(
        'https://www.googleapis.com/youtube/v3/playlistItems',
        method='POST',
        raise_error=False,
        headers=headers,
        data=json.dumps({
            'part': 'snippet',
            'body': {
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        }))
    shared_state['requests_remaining'] -= 1
    if shared_state['requests_remaining'] == 0:
        io_loop.stop()
    return response
