'''Top-level functions for querying Facebook and updating YouTube'''
from chineurs import (
    celery,
    facebook_group,
    storage,
    timestamp)


def update(user_id, group_id, playlist_id):
    '''Queries Facebook for new videos based on timestamp
       and updates YouTube'''
    timestamp_handler = timestamp.TimestampHandler(playlist_id, group_id)
    latest = timestamp_handler.read()
    user = storage.get_user_by_id(user_id)  # pylint:disable=E1120
    ids = list(facebook_group.get_youtube_links(
        group_id, user['fb_access_token'], latest))
    timestamp_handler.write()
    job_id = storage.new_job()  # pylint:disable=E1120
    headers = {}
    user['google_credentials'].apply(headers)
    celery.insert_videos.delay(
        job_id,
        headers,
        playlist_id,
        ids)
    return job_id
