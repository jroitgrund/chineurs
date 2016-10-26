'''Tests for celery'''
from unittest.mock import patch

from chineurs import celery


@patch('chineurs.celery.updates', autospec=True)
def test_insert_videos(updates):
    '''Inserts videos and updates progress'''
    celery.update(1, 'group', 'playlist', 'task_uuid')
    updates.update.assert_called_once_with(1, 'group', 'playlist', 'task_uuid')
