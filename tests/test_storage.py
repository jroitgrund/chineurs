'''Tests for storage'''
from unittest.mock import patch

from pyfakefs import fake_filesystem_unittest

from chineurs.storage import Storage


class TestStorage(fake_filesystem_unittest.TestCase):
    '''Tests for Storage'''

    def setUp(self):
        self.setUpPyfakefs()

    @patch('chineurs.settings.DATA_DIRECTORY', '/data')
    def test_read_absent(self):  # pylint:disable=no-self-use
        '''Absent keys return None'''
        assert Storage('foo').get('bar') is None

    @patch('chineurs.settings.DATA_DIRECTORY', '/data')
    def test_read_write(self):  # pylint:disable=no-self-use
        '''Can read and write values'''
        storage = Storage('foo')
        storage.set('key', 'value')
        assert storage.get('key') == 'value'
