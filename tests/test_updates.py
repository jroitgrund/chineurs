'''Tests for updates module'''
from datetime import datetime
from unittest.mock import call, Mock, patch

import pytz

from chineurs import updates


@patch('chineurs.updates.storage', spec=True)
@patch('chineurs.updates.celery', autospec=True)
@patch('chineurs.updates.facebook_group', autospec=True)
@patch('chineurs.timestamp.TimestampHandler', autospec=True)
def test_update(  # pylint:disable=C0103
        mock_timestamp_handler,
        facebook_group,
        celery,
        storage):
    '''Update gets YouTube links with the correct timestamp and playlist
        contents'''
    now = datetime.now(pytz.utc)
    mock_timestamp_handler.return_value.read.return_value = now
    facebook_group.get_youtube_links.return_value = ['dasfdasfda']

    def set_headers(headers):
        '''Sets headers like google credentials'''
        headers['auth'] = True
    credentials = Mock()
    credentials.apply.side_effect = set_headers
    storage.get_user_by_id.return_value = {
        'google_credentials': credentials,
        'fb_access_token': 'fb'
    }

    storage.new_job.return_value = 'task_uuid'

    assert updates.update('uuid', 'group', 'playlist') == 'task_uuid'

    mock_timestamp_handler.return_value.read.assert_has_calls([call()])
    facebook_group.get_youtube_links.assert_called_once_with(
        'group', 'fb', now)
    celery.insert_videos.delay.assert_called_once_with(
        'task_uuid', {'auth': True}, 'playlist', ['dasfdasfda'])
