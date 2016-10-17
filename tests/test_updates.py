'''Tests for updates module'''
from unittest.mock import Mock, patch

from chineurs import updates


@patch('chineurs.updates.authentication', autospec=True)
@patch('chineurs.updates.youtube_playlist', autospec=True)
@patch('chineurs.updates.facebook_group', autospec=True)
@patch('chineurs.timestamp.TimestampHandler', autospec=True)
def test_update(  # pylint:disable=C0103
        mock_timestamp_handler,
        facebook_group,
        youtube_playlist,
        authentication):
    '''Update gets YouTube links with the correct timestamp and playlist
        contents'''
    mock_timestamp_handler_instance = Mock()
    mock_timestamp_handler.return_value = mock_timestamp_handler_instance
    mock_timestamp_handler_instance.read.return_value = 'latest'
    facebook_group.get_youtube_links.return_value = [
        'youtube.com/watch?v=dasfdasfda&']
    # youtube_playlist.list_playlist_contents.return_value = ['bar']
    authentication.get_facebook_access_token.return_value = 'fb'
    authentication.get_google_credentials.return_value = 'g'

    assert updates.update('uuid', 'group', 'playlist') == [
        'youtube.com/watch?v=dasfdasfda&']

    mock_timestamp_handler.assert_called_once_with('uuid', 'group')
    authentication.get_facebook_access_token.assert_called_once_with('uuid')
    authentication.get_google_credentials.assert_called_once_with('uuid')
    facebook_group.get_youtube_links.assert_called_once_with(
        'group', 'fb', 'latest')
    youtube_playlist.insert_videos.assert_called_once_with(
        'g', 'playlist', ['dasfdasfda'])
