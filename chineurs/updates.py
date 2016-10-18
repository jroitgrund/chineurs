'''Top-level functions for querying Facebook and updating YouTube'''
import uuid

from chineurs import (
    authentication,
    celery,
    facebook_group,
    timestamp)


def update(session_uuid, group_id, playlist_id):
    '''Queries Facebook for new videos based on timestamp
       and updates YouTube'''
    timestamp_handler = timestamp.TimestampHandler(session_uuid, group_id)
    latest = timestamp_handler.read()
    facebook_access_token = authentication.get_facebook_access_token(
        session_uuid)
    google_credentials = authentication.get_google_credentials(session_uuid)
    ids = list(facebook_group.get_youtube_links(
        group_id, facebook_access_token, latest))
    task_uuid = str(uuid.uuid4())
    headers = {}
    google_credentials.apply(headers)
    celery.insert_videos.delay(
        task_uuid,
        headers,
        playlist_id,
        ids)
    timestamp_handler.write()
    return task_uuid
