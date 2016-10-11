"""Gets or sets the last read post timestamp"""
import os

from datetime import datetime
from group_feed import FACEBOOK_TIMESTAMP_FORMAT
import pytz


def get_last_timestamp():
    """Gets the last timestamp or the first date ever
    from the timestamp file"""
    if os.path.isdir('data') and os.path.isfile('data/timestamp.txt'):
        with open('data/timestamp.txt') as handle:
            timestamp = list(handle)[0]
        return timestamp
    return '0001-01-01T00:00:00+0000'


def write_last_timestamp():
    """Writes the current date to the timestamp file"""
    if not os.path.isdir('data'):
        os.makedirs('data')
    with open('data/timestamp.txt', 'w') as handle:
        handle.write(datetime.now(pytz.utc).strftime(
            FACEBOOK_TIMESTAMP_FORMAT))
