'''Tests for timestamp module'''
from datetime import datetime
from unittest.mock import patch

from chineurs import timestamp


@patch('chineurs.timestamp.datetime')
@patch('chineurs.timestamp.storage', spec=True)
# pylint: disable=R0201
def test_read_write(mock_storage, mock_datetime):
    '''Reads the timestamp from the file and writes the date at
       time of reading'''
    now = datetime.now()
    now2 = datetime.now()
    mock_datetime.now.return_value = now2
    mock_storage.get_last_playlist_insert.return_value = now

    timestamp_handler = timestamp.TimestampHandler('playlist', 'group')

    assert timestamp_handler.read() is now

    timestamp_handler.write()

    mock_storage.set_last_playlist_insert.assert_called_once_with(
        'playlist', 'group', now2)
