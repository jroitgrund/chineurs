'''Worker for asynchronous tasks'''
from celery import Celery

from chineurs import settings, storage, youtube_playlist

CELERY_APP = Celery('tasks', broker=settings.CELERY_BROKER)
CELERY_APP.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json')


@CELERY_APP.task
def insert_videos(uuid, headers, playlist_id, video_ids):
    '''Inserts videos synchronously and writes to storage when done'''
    percent = 0
    for i, video_id in enumerate(video_ids):
        youtube_playlist.insert_video(headers, playlist_id, video_id)
        new_percent = 100 * (i + 1) / len(video_ids)
        if new_percent > percent:
            percent = new_percent
            storage.save_job_progress(uuid, percent)  # pylint:disable=E1120
