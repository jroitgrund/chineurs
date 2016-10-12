"""Gets or sets the last read post timestamp"""
from datetime import datetime
import os

import pytz

from chineurs.group_feed import FACEBOOK_TIMESTAMP_FORMAT


def get_last_timestamp():
    """Gets the last timestamp or the first date ever
    from the timestamp file"""
    data_dir_path = get_data_dir_path()
    timestamp_file_path = os.path.join(data_dir_path, 'timestamp.txt')
    if os.path.isdir(data_dir_path) and os.path.isfile(
            timestamp_file_path):
        with open(timestamp_file_path) as handle:
            timestamp = list(handle)[0]
        return timestamp
    return '0001-01-01T00:00:00+0000'


def write_last_timestamp():
    """Writes the current date to the timestamp file"""
    if not os.path.isdir('data'):
        os.makedirs('data')
    timestamp_file_path = os.path.join(get_data_dir_path(), 'timestamp.txt')
    with open(timestamp_file_path, 'w') as handle:
        handle.write(datetime.now(pytz.utc).strftime(
            FACEBOOK_TIMESTAMP_FORMAT))


def get_data_dir_path():
    """Gets the path to the data directory"""
    return os.path.join(os.path.dirname(__file__), '..', 'data')
