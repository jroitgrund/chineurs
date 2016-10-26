'''Worker for asynchronous tasks'''
from celery import Celery

from chineurs import settings, updates

CELERY_APP = Celery('tasks', broker=settings.CELERY_BROKER)
CELERY_APP.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json')


@CELERY_APP.task
def update(user_id, group_id, playlist_id, job_id):
    '''Runs update in Celery'''
    updates.update(user_id, group_id, playlist_id, job_id)
