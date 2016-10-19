'''Entry point for chineurs server'''
import functools
import urllib

from flask import jsonify, redirect, render_template, request, session, url_for

from chineurs import (
    authentication,
    facebook_group,
    storage,
    updates)
from chineurs.app import APP


@APP.errorhandler(facebook_group.ExpiredFacebookToken)
def handle_expired_facebook_token(error):  # pylint:disable=unused-argument
    '''Handles expired facebook tokens'''
    APP.logger.info(
        'Facebook token expired, redirecting from {}'.format(request.url))
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
    return render_template('index.html', update_url=url_for('update'))


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


@APP.route('/update')
def update():
    '''Uploads all new videos to YouTube'''
    return '{}'.format(updates.update(
        session['user_id'],
        request.args.get('group_id'),
        request.args.get('playlist_id')))


@APP.route('/done/<task_uuid>')
def done(task_uuid):
    '''Checks if a given youtube upload request if done'''
    # pylint:disable=E1120
    return jsonify(progress=storage.get_job_progress(task_uuid))
    # pylint:enable=E1120


def full_url(route):
    '''Returns an absolute URL using the host in the request'''
    parts = urllib.parse.urlparse(request.url)
    scheme = parts[0]
    netloc = parts[1]
    return urllib.parse.urlunparse(
        [scheme, netloc, url_for(route), None, None, None])
