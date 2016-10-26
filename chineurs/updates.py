'''Top-level functions for querying Facebook and updating YouTube'''
from collections import OrderedDict
import functools
from itertools import chain

import tornado

from chineurs import (
    facebook_group,
    storage,
    timestamp,
    youtube_playlist)


def update(user_id, group_id, playlist_id, job_id):
    '''Queries Facebook for new videos based on timestamp
       and updates YouTube'''
    user = storage.get_user_by_id(user_id)  # pylint:disable=E1120
    timestamp_handler = timestamp.TimestampHandler(playlist_id, group_id)
    latest = timestamp_handler.read()

    video_ids_by_post = facebook_group.get_youtube_links(
        group_id, user['fb_access_token'], latest)
    timestamp_handler.write()

    tornado.ioloop.IOLoop.current().run_sync(functools.partial(
        add_video_ids_from_comments,
        video_ids_by_post,
        user['fb_access_token'],
        job_id))
    video_ids = list(chain.from_iterable(reversed(video_ids_by_post.values())))

    headers = {}
    user['google_credentials'].apply(headers)

    insert_videos(
        job_id,
        headers,
        playlist_id,
        unique_in_same_order(video_ids))
    return job_id


def unique_in_same_order(items):
    '''Return items de-duplicated, in the same order'''
    return list(OrderedDict.fromkeys(items).keys())


async def add_video_ids_from_comments(video_ids_by_post, access_token, job_id):
    '''Fetches videos from comments for each post'''
    # pylint:disable=E1120
    percent = 0
    for i, post_id in enumerate(video_ids_by_post.keys()):
        video_ids_by_post[post_id].extend(
            await facebook_group.get_youtube_links_from_comments(
                post_id, access_token))
        new_percent = 100 * (i + 1) / len(video_ids_by_post)
        if new_percent > percent:
            percent = new_percent
            storage.save_job_progress(job_id, percent, 'facebook')
    storage.save_job_progress(job_id, 100, 'facebook')


def insert_videos(job_id, headers, playlist_id, video_ids):
    '''Inserts videos synchronously and writes to storage when done'''
    # pylint:disable=E1120
    percent = 0
    for i, video_id in enumerate(video_ids):
        youtube_playlist.insert_video(headers, playlist_id, video_id)
        new_percent = 100 * (i + 1) / len(video_ids)
        if new_percent > percent:
            percent = new_percent
            storage.save_job_progress(job_id, percent, 'youtube')
    storage.save_job_progress(job_id, 100, 'youtube')
