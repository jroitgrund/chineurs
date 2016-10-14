'''Tests for timestamp module'''
from unittest.mock import Mock, patch

from pyfakefs import fake_filesystem_unittest

from chineurs import timestamp


class TestTimestampHandler(fake_filesystem_unittest.TestCase):
    '''Tests for TimestampHandler'''

    @patch('chineurs.timestamp.datetime')
    @patch('chineurs.timestamp.Storage', autospec=True)
    # pylint: disable=R0201
    def test_read_write(self, mock_storage, mock_datetime):
        '''Reads the timestamp from the file and writes the date at
           time of reading'''
        current_time = Mock(['strftime'])
        mock_datetime.now.return_value = current_time
        current_time.strftime.return_value = 'new_timestamp'
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get.return_value = 'timestamp'

        timestamp_handler = timestamp.TimestampHandler('group', 'uuid')

        mock_storage.assert_called_once_with('uuid')
        assert timestamp_handler.read() is 'timestamp'
        mock_storage_instance.get.assert_called_once_with('timestamp-group')

        timestamp_handler.write()

        mock_storage_instance.set.assert_called_once_with(
            'timestamp-group', 'new_timestamp')

    @patch('chineurs.timestamp.datetime')
    @patch('chineurs.timestamp.Storage', autospec=True)
    # pylint:disable=unused-argument,no-self-use
    def test_read_no_existing(self, mock_storage, mock_datetime):
        '''Returns default timestamp when no file exists yet'''
        mock_storage_instance = Mock()
        mock_storage.return_value = mock_storage_instance
        mock_storage_instance.get.return_value = None

        timestamp_handler = timestamp.TimestampHandler('group', 'uuid')

        mock_storage.assert_called_once_with('uuid')
        assert timestamp_handler.read() is timestamp.DEFAULT_TIMESTAMP
        mock_storage_instance.get.assert_called_once_with('timestamp-group')
