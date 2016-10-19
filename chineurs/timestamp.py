'''Gets or sets the last read post timestamp'''
from datetime import datetime

import pytz

from chineurs import storage

DEFAULT_DATETIME = datetime(1, 1, 1, 0, 0, 0, 0, pytz.utc)


class TimestampHandler:
    '''Handles timestamping for a group by remembering the date at which
       the last timestamp was read'''

    def __init__(self, playlist_id, group_id):
        self.playlist_id = playlist_id
        self.group_id = group_id

    def read(self):
        '''Reads the latest timestamp and stores the current datetime'''

        self.last_read = datetime.now(pytz.utc)  # pylint:disable=W0201
        # pylint:disable=E1120
        last_playlist_insert = storage.get_last_playlist_insert(
            self.playlist_id, self.group_id)
        # pylint:enable=E1120
        return last_playlist_insert or DEFAULT_DATETIME

    def write(self):
        '''Writes the last read datetime'''
        storage.set_last_playlist_insert(  # pylint:disable=E1120
            self.playlist_id, self.group_id, self.last_read)
