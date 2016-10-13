'''Tests for timestamp module'''
from unittest.mock import Mock, patch

from pyfakefs import fake_filesystem_unittest

from chineurs import timestamp


class TestTimestampHandler(fake_filesystem_unittest.TestCase):
    '''Tests for TimestampHandler'''

    def setUp(self):
        self.setUpPyfakefs()
        self.data_directory = timestamp.settings.DATA_DIRECTORY = '/data'

    def tearDown(self):
        timestamp.settings.DATA_DIRECTORY = self.data_directory

    @patch('chineurs.timestamp.datetime')
    def test_read_write(self, mock_datetime):
        '''Reads the timestamp from the file and writes the date at
           time of reading'''
        self.fs.CreateFile('/data/group', contents='timestamp\n')
        current_time = Mock(['strftime'])
        mock_datetime.now.return_value = current_time
        current_time.strftime.return_value = 'new_timestamp'
        timestamp_handler = timestamp.TimestampHandler('group')

        assert timestamp_handler.read() == 'timestamp'
        timestamp_handler.write()

        with open('/data/group') as handle:
            assert handle.read().strip() == 'new_timestamp'

    def test_read_no_file(self):  # pylint: disable=R0201
        '''Returns the default when the file is not readable'''
        timestamp_handler = timestamp.TimestampHandler('group')

        assert timestamp_handler.read() == timestamp.DEFAULT_TIMESTAMP
