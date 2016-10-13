from chineurs import facebook_group, timestamp


def update(
        facebook_access_token,
        group_id,
        google_access_token,
        playlist_id):
    timestamp_handler = timestamp.TimestampHandler(group_id)
    latest = timestamp_handler.read()
    urls = facebook_group.get_youtube_links(
        group_id, facebook_access_token, latest)
    timestamp_handler.write()
    return urls
