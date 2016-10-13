'''Top-level functions for querying Facebook and updating YouTube'''
from chineurs import facebook_group, timestamp


def update(
        facebook_access_token,
        group_id,
        google_access_token,  # pylint: disable=unused-argument
        playlist_id):  # pylint: disable=unused-argument
    '''Queries Facebook for new videos based on timestamp
       and updates YouTube'''
    timestamp_handler = timestamp.TimestampHandler(group_id)
    latest = timestamp_handler.read()
    urls = facebook_group.get_youtube_links(
        group_id, facebook_access_token, latest)
    timestamp_handler.write()
    return urls
