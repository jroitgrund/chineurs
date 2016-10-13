from unittest.mock import Mock, patch

from chineurs import timestamp, updates


@patch('chineurs.facebook_group.get_youtube_links', autospec=True)
@patch('chineurs.timestamp.TimestampHandler', autospec=True)
def test_update(TimestampHandler, get_youtube_links):
    mock_timestamp_handler = Mock(spec=timestamp.TimestampHandler)
    TimestampHandler.return_value = mock_timestamp_handler
    mock_timestamp_handler.read.return_value = 'latest'
    get_youtube_links.return_value = ['foo']

    assert updates.update('fb', 'group', 'g', 'playlist') == ['foo']

    TimestampHandler.assert_called_once_with('group')
    get_youtube_links.assert_called_once_with('group', 'fb', 'latest')
