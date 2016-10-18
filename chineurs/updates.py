'''Top-level functions for querying Facebook and updating YouTube'''

from chineurs import (
    authentication,
    facebook_group,
    timestamp,
    youtube_playlist)


def update(uuid, group_id, playlist_id):
    '''Queries Facebook for new videos based on timestamp
       and updates YouTube'''
    timestamp_handler = timestamp.TimestampHandler(uuid, group_id)
    latest = timestamp_handler.read()
    facebook_access_token = authentication.get_facebook_access_token(uuid)
    google_credentials = authentication.get_google_credentials(uuid)
    ids = list(facebook_group.get_youtube_links(
        group_id, facebook_access_token, latest))
    youtube_playlist.insert_videos(
        google_credentials,
        playlist_id,
        ids)
    timestamp_handler.write()
    return ids
