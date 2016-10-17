'''Functions to interact with YouTube playlists'''
import functools
import json

from tornado.httpclient import AsyncHTTPClient
import tornado.gen
import tornado.ioloop

from chineurs.app import APP


def log_error(response):
    '''Log a  response'''
    APP.logger.error(response)


def insert_videos(credentials, playlist_id, video_ids):
    '''Runs the helper in an io loop'''
    responses = tornado.ioloop.IOLoop.current().run_sync(functools.partial(
        insert_videos_helper, credentials, playlist_id, video_ids))
    map(lambda response: response.rethrow(), responses)


async def insert_videos_helper(credentials, playlist_id, video_ids):
    '''Inserts videos in a playlist asynchronously'''
    return await tornado.gen.multi([
        insert_video(credentials, playlist_id, video_id)
        for video_id in video_ids])


async def insert_video(credentials, playlist_id, video_id):
    '''Inserts a video in a playlist'''
    http_client = AsyncHTTPClient()
    headers = {}
    credentials.apply(headers)
    response = await http_client.fetch(
        'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet',
        method='POST',
        raise_error=False,
        headers=headers,
        body=json.dumps({
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }))
    return response
