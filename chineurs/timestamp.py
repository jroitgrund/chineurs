'''Gets or sets the last read post timestamp'''
from datetime import datetime
import os

import pytz

from chineurs import facebook_group, settings

DEFAULT_TIMESTAMP = '0001-01-01T00:00:00+0000'


class TimestampHandler:
    '''Handles timestamping for a group by remembering the date at which
       the last timestamp was read'''

    def __init__(self, group_id):
        self.timestamp_path = os.path.join(settings.DATA_DIRECTORY, group_id)
        self.last_read = None

    def read(self):
        '''Reads the latest timestamp and stores the current datetime'''
        self.last_read = datetime.now(pytz.utc)
        if os.path.isfile(self.timestamp_path):
            with open(self.timestamp_path) as handle:
                return handle.read().strip()
        return DEFAULT_TIMESTAMP

    def write(self):
        '''Writes the last read datetime'''
        with open(self.timestamp_path, 'w') as handle:
            print('foo')
            print(self.last_read.strftime('YYYY'))
            handle.write(self.last_read.strftime(
                facebook_group.FACEBOOK_TIMESTAMP_FORMAT))
