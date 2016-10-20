'''SQL abstraction'''
from functools import wraps
import pickle

import psycopg2


USER_COLS = ['id', 'facebook_id', 'fb_access_token', 'google_credentials']


def get_db():
    '''Opens a new database connection if there is none yet for the
    current application context.
    '''
    return psycopg2.connect('dbname=chinema user=chinema')


def commit(connection):
    '''Wrapper around commit to enable mocking'''
    connection.commit()


def close(connection):
    '''Wrapper around close to enable mocking'''
    connection.close()


def transactional(db_function):
    '''Wraps a database-using function in a transaction'''
    @wraps(db_function)
    def transactional_fun(*args, **kwargs):
        '''Transaction-wrapped DB function'''
        connection = get_db()
        with connection.cursor() as cursor:
            result = db_function(cursor, *args, **kwargs)
            commit(connection)
            close(connection)
            return result

    return transactional_fun


@transactional
def get_user_id(cursor, facebook_id, access_token):
    '''Gets a user id (new or existing) from an facebook_id'''
    cursor.execute(
        'UPDATE users SET fb_access_token=%s WHERE facebook_id=%s RETURNING id',
        (access_token, facebook_id))
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            'INSERT INTO '
            'users(facebook_id, fb_access_token) '
            'VALUES (%s, %s) RETURNING id',
            (facebook_id, access_token))
        user = cursor.fetchone()
    return user[0]


@transactional
def set_user_facebook_access_token(cursor, user_id, token):
    '''Stores a facebook access token for a user'''
    cursor.execute(
        'UPDATE users SET fb_access_token=%s WHERE id=%s', (token, user_id))


@transactional
def set_user_google_credentials(cursor, user_id, credentials):
    '''Stores google credentials for a user'''
    cursor.execute(
        'UPDATE users SET google_credentials=%s WHERE id=%s',
        (pickle.dumps(credentials), user_id))


@transactional
def get_user_by_id(cursor, user_id):
    '''Gets user details by user id'''
    cursor.execute(
        'SELECT * FROM users WHERE id=%s', (user_id,))
    user = row_to_dict(
        USER_COLS,
        cursor.fetchone())
    user['google_credentials'] = (
        user['google_credentials'] and
        pickle.loads(user['google_credentials']))
    return user


@transactional
def get_last_playlist_insert(cursor, playlist_id, group_id):
    '''Gets the datetime a group was last inserted into a playlist'''
    cursor.execute(
        'SELECT datetime FROM playlist_inserts '
        'WHERE playlist_id=%s AND group_id=%s',
        (playlist_id, group_id))
    row = cursor.fetchone()
    return row and row[0]


@transactional
def set_last_playlist_insert(cursor, playlist_id, group_id, datetime):
    '''Sets the time a group was last inserted into a playlist'''
    cursor.execute(
        'UPDATE playlist_inserts SET datetime=%s '
        'WHERE playlist_id=%s AND group_id=%s returning datetime',
        (datetime, playlist_id, group_id))
    if not cursor.fetchone():
        cursor.execute(
            'INSERT INTO playlist_inserts(playlist_id, group_id, datetime)'
            'VALUES (%s, %s, %s)', (playlist_id, group_id, datetime))


@transactional
def new_job(cursor):
    '''Adds info about a running job'''
    cursor.execute(
        'INSERT INTO '
        'jobs(progress) '
        'VALUES (%s) RETURNING id',
        (0,))
    return cursor.fetchone()[0]


@transactional
def get_job_progress(cursor, job_id):
    '''Gets the progress of a running job'''
    cursor.execute(
        'SELECT progress FROM jobs '
        'WHERE id=%s', (job_id,))
    progress = cursor.fetchone()[0]
    if progress == 100:
        cursor.execute(
            'DELETE FROM jobs WHERE id=%s', (job_id,))
    return progress


@transactional
def save_job_progress(cursor, job_id, progress):
    '''Saves the progress of a running job'''
    cursor.execute(
        'UPDATE jobs SET progress=%s '
        'WHERE id=%s', (progress, job_id))


def row_to_dict(column_names, row):
    '''Converts an sql row to a dict with matching column names'''
    return dict(zip(column_names, row))
