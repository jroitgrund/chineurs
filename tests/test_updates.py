'''Tests for updates module'''
from collections import OrderedDict
from datetime import datetime
from unittest.mock import call, Mock, patch

import pytz

from chineurs import updates


@patch('chineurs.updates.storage', spec=True)
@patch('chineurs.updates.youtube_playlist', autospec=True)
@patch('chineurs.updates.facebook_group', autospec=True)
@patch('chineurs.timestamp.TimestampHandler', autospec=True)
def test_update(  # pylint:disable=C0103
        mock_timestamp_handler,
        facebook_group,
        youtube_playlist,
        storage):
    '''Update gets YouTube links with the correct timestamp and playlist
        contents'''
    now = datetime.now(pytz.utc)
    mock_timestamp_handler.return_value.read.return_value = now
    facebook_group.get_youtube_links.return_value = OrderedDict([
        ('post_id', ['link1']),
    ])

    # pylint:disable=W0613,C0111
    async def async_get(post_id, token):
        return ['link2']
    facebook_group.get_youtube_links_from_comments.side_effect = async_get
    # pylint:enable=W0613,C0111

    def set_headers(headers):
        '''Sets headers like google credentials'''
        headers['auth'] = True

    credentials = Mock()
    credentials.apply.side_effect = set_headers
    storage.get_user_by_id.return_value = {
        'google_credentials': credentials,
        'fb_access_token': 'fb'
    }

    updates.update(1, 'group', 'playlist', 'task_uuid')

    mock_timestamp_handler.return_value.read.assert_has_calls([call()])
    facebook_group.get_youtube_links.assert_called_once_with(
        'group', 'fb', now)
    facebook_group.get_youtube_links_from_comments.assert_called_once_with(
        'post_id', 'fb')
    youtube_playlist.insert_video.assert_has_calls([
        call({'auth': True}, 'playlist', 'link1'),
        call({'auth': True}, 'playlist', 'link2'),
    ])
