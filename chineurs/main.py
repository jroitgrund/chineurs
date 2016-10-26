'''Entry point for chineurs server'''
from concurrent.futures import ThreadPoolExecutor
import functools
import json
import urllib

from flask import jsonify, redirect, render_template, request, session, url_for

from chineurs import (
    authentication,
    celery,
    facebook_group,
    resources,
    storage,
    youtube_playlist)
from chineurs.app import APP


@APP.errorhandler(authentication.AuthExpired)
def handle_expired_credentials(error):  # pylint:disable=unused-argument
    '''Handles expired credentials'''
    APP.logger.exception(
        'Auth expired, redirecting from {}'.format(request.url))
    return redirect(authentication.get_facebook_authentication_uri(
        full_url('facebook')))


def user_id_required(route):
    '''Wraps a route to require a UUID and redirect if not present'''
    @functools.wraps(route)
    def decorated_route(*args, **kwargs):
        '''Checks if user_id is in session, redirects to authenticate if not'''
        if 'user_id' not in session:
            APP.logger.info(
                'No user id, redirecting from {}'.format(request.url))
            return redirect(
                authentication.get_facebook_authentication_uri(
                    full_url('facebook')))
        return route(*args, **kwargs)
    return decorated_route


@APP.route('/logout')
def logout():
    '''Clears session'''
    APP.logger.info('Clearing UUID')
    session.clear()
    return redirect(url_for('home'))


@APP.route('/')
@user_id_required
def home():
    '''Home page'''
    user = storage.get_user_by_id(session['user_id'])  # pylint:disable=E1120
    headers = {}
    user['google_credentials'].apply(headers)
    executor = ThreadPoolExecutor(max_workers=2)
    fb_groups = executor.submit(lambda: facebook_group.get_groups(
        user['fb_access_token']))
    playlists = executor.submit(lambda: youtube_playlist.get_playlists(
        headers))
    return render_template(
        'index.html',
        resources=resources.get_resources(),
        data=json.dumps({
            'update_url': url_for('update'),
            'facebook_groups': fb_groups.result(),
            'youtube_playlists': playlists.result()}))


@APP.route('/facebook')
def facebook():
    '''Gets the Facebook auth token and stores it in cookies'''
    session['user_id'] = authentication.save_facebook_access_token(
        request.args.get('code'),
        full_url('facebook'))
    return redirect(
        authentication.get_google_authentication_uri(full_url('google')))


@APP.route('/google')
def google():
    '''Saves Google credentials'''
    authentication.save_google_credentials(
        session['user_id'],
        request.args.get('code'),
        full_url('google'))
    return redirect(url_for('home'))


@APP.route('/update', methods=['POST'])
def update():
    '''Uploads all new videos to YouTube'''
    task_uuid = storage.new_job()  # pylint:disable=E1120
    celery.update.delay(
        session['user_id'],
        request.get_json()['group_id'],
        request.get_json()['playlist_id'],
        task_uuid)
    return jsonify({'done_url': url_for('done', task_uuid=task_uuid)})


@APP.route('/done/<task_uuid>')
def done(task_uuid):
    '''Checks if a given youtube upload request if done'''
    # pylint:disable=E1120
    return jsonify(storage.get_job_progress(task_uuid))
    # pylint:enable=E1120


def full_url(route):
    '''Returns an absolute URL using the host in the request'''
    parts = urllib.parse.urlparse(request.url)
    scheme = parts[0]
    netloc = parts[1]
    return urllib.parse.urlunparse(
        [scheme, netloc, url_for(route), None, None, None])


# if APP.debug:
#     from werkzeug.contrib.profiler import ProfilerMiddleware
#     APP = ProfilerMiddleware(APP, open('profile', 'w'))
