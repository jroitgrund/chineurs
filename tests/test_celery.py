'''Tests for celery'''
from unittest.mock import call, patch

from chineurs import celery


@patch('chineurs.celery.storage', spec=True)
@patch('chineurs.celery.youtube_playlist', autospec=True)
def test_insert_videos(youtube_playlist, storage):
    '''Inserts videos and updates progress'''
    celery.insert_videos('uuid', {}, 'playlist', range(5))

    youtube_playlist.insert_video.assert_has_calls(
        call({}, 'playlist', i) for i in range(5))

    storage.save_job_progress.assert_has_calls(
        call('uuid', percent) for percent in [20, 40, 60, 80, 100])
