'''Gets or sets the last read post timestamp'''
from datetime import datetime

import pytz

from chineurs import facebook_group
from chineurs.storage import Storage

DEFAULT_TIMESTAMP = '0001-01-01T00:00:00+0000'


class TimestampHandler:
    '''Handles timestamping for a group by remembering the date at which
       the last timestamp was read'''

    def __init__(self, group_id, uuid):
        self.storage = Storage(uuid)
        self.key = 'timestamp-{}'.format(group_id)
        self.last_read = None

    def read(self):
        '''Reads the latest timestamp and stores the current datetime'''
        self.last_read = datetime.now(pytz.utc)
        return self.storage.get(self.key) or DEFAULT_TIMESTAMP

    def write(self):
        '''Writes the last read datetime'''
        self.storage.set(self.key, self.last_read.strftime(
            facebook_group.FACEBOOK_TIMESTAMP_FORMAT))
