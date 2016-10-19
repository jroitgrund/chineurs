'''Tests for storage'''
from datetime import datetime
from unittest.mock import Mock, patch

import psycopg2
import pytz
from yoyo import read_migrations, get_backend

from chineurs import settings, storage


# pylint:disable=W0201,E1120
# pylint:disable=unused-argument,no-self-use


class DummyCredentials:  # pylint:disable=R0903
    '''Dummy object for google credentials'''

    def __init__(self):
        self.result = 5

    def check_credentials(self):
        '''Checks a dummy credentials is a valid instance'''
        assert self.result == 5


def do_nothing(*args, **kwargs):
    '''Just do nothing'''
    pass


class TestStorage:
    '''Tests for storage'''
    @classmethod
    def setup_class(cls):
        '''Set up schema and mocks'''
        url = 'postgres://{}@{}:5432/{}'.format(
            settings.TEST_POSTGRES_USER or 'ubuntu',
            settings.TEST_POSTGRES_HOST or '127.0.0.1',
            settings.TEST_POSTGRES_DB or 'circle_test')
        backend = get_backend(url)
        migrations = read_migrations('migrations')
        backend.apply_migrations(backend.to_apply(migrations))
        cls.commit_patch = patch('chineurs.storage.commit', do_nothing)
        cls.close_patch = patch('chineurs.storage.close', do_nothing)
        cls.commit_patch.start()
        cls.close_patch.start()

    @classmethod
    def teardown_class(cls):
        '''Removes patches'''
        cls.commit_patch.stop()
        cls.close_patch.stop()

    def setup_method(self, method):
        '''Set up and patch connection'''
        if settings.TEST_POSTGRES_HOST == '':
            host = ''
        else:
            host = ' host={}'.format(
                settings.TEST_POSTGRES_HOST or '127.0.0.1')
        self.connection = psycopg2.connect('dbname={} user={}{}'.format(
            settings.TEST_POSTGRES_DB or 'circle_test',
            settings.TEST_POSTGRES_USER or 'ubuntu',
            host))
        self.get_db_patch = patch(
            'chineurs.storage.get_db', Mock(return_value=self.connection))
        self.get_db_patch.start()

    def teardown_method(self, method):
        '''Close and rollback connection and patch'''
        self.connection.rollback()
        self.connection.close()
        self.get_db_patch.stop()

    def test_get_user_id_absent(self):
        '''Get user id creates a new ID'''
        storage.get_user_id('foo@bar.com', 'access_token')
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM users')
            assert cursor.fetchone()[0] == 1

    def test_get_user_id_present(self):
        '''Get user id returns an existing ID'''
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users(facebook_id, id) VALUES (%s, %s)',
                ('foo@bar.com', 5))
            assert storage.get_user_id('foo@bar.com', 'access_token') == 5
            cursor.execute('SELECT COUNT(*) FROM users')
            assert cursor.fetchone()[0] == 1

    def test_user(self):
        '''Tests setting and getting user info'''
        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users(facebook_id) '
                'VALUES (%s) RETURNING id',
                ('foo@bar.com',))
            user_id = cursor.fetchone()[0]
            storage.set_user_facebook_access_token(user_id, 'token')
            storage.set_user_google_credentials(user_id, DummyCredentials())
            user = storage.get_user_by_id(user_id)
            assert user['fb_access_token'] == 'token'
            user['google_credentials'].check_credentials()

    def test_playlist_inserts(self):
        '''Tests setting and getting last insert info'''
        now = datetime.now(pytz.utc)
        storage.set_last_playlist_insert('playlist', 'group', now)
        assert storage.get_last_playlist_insert('playlist', 'group') == now

    def test_jobs(self):
        '''Tests job methods'''
        with self.connection.cursor() as cursor:
            job_id = storage.new_job()
            assert storage.get_job_progress(job_id) == 0
            storage.save_job_progress(job_id, 100)
            assert storage.get_job_progress(job_id) == 100
            cursor.execute('SELECT COUNT(*) FROM jobs')
            assert cursor.fetchone()[0] == 0

    def test_facebook_groups(self):
        '''Tests facebook group methods'''
        user_id = storage.get_user_id('id', 'token')
        storage.save_facebook_groups(
            user_id, [
                {
                    'name': 'name1',
                    'id': 'id1'
                },
                {
                    'name': 'name2',
                    'id': 'id2'
                }])
        assert storage.get_facebook_groups(user_id) == [
            {
                'name': 'name1',
                'id': 'id1'
            },
            {
                'name': 'name2',
                'id': 'id2'
            }]
