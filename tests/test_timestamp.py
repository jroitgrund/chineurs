from datetime import datetime
from unittest.mock import Mock, patch

from pyfakefs import fake_filesystem_unittest

from chineurs import timestamp


class TestTimestampHandler(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    @patch('chineurs.timestamp.datetime')
    @patch('chineurs.settings.DATA_DIRECTORY', '/data')
    def test_read_write(self, mock_datetime):
        self.fs.CreateFile('/data/group', contents='timestamp\n')
        current_time = Mock(['strftime'])
        mock_datetime.now.return_value = current_time
        current_time.strftime.return_value = 'new_timestamp'
        timestamp_handler = timestamp.TimestampHandler('group')

        assert timestamp_handler.read() == 'timestamp'
        timestamp_handler.write()

        with open('/data/group') as handle:
            assert handle.read().strip() == 'new_timestamp'

    def test_read_no_file(self):
        timestamp_handler = timestamp.TimestampHandler('group')

        assert timestamp_handler.read() == timestamp.DEFAULT_TIMESTAMP
