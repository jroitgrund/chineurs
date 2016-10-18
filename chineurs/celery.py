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
    youtube_playlist.insert_videos(headers, playlist_id, video_ids)
    storage.Storage(uuid).set('done', 'True')
