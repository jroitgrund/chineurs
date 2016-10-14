'''Entry point for chineurs server'''
import functools
import urllib
import uuid

from flask import redirect, render_template, request, session, url_for

from chineurs import (
    authentication,
    facebook_group,
    updates)
from chineurs.app import APP


@APP.errorhandler(facebook_group.ExpiredFacebookToken)
def handle_expired_facebook_token(error):  # pylint:disable=unused-argument
    '''Handles expired facebook tokens'''
    APP.logger.info(
        'Facebook token expired, redirecting from {}'.format(request.url))
    return redirect(authentication.get_facebook_authentication_uri(
        full_url('facebook')))


def uuid_required(route):
    '''Wraps a route to require a UUID and redirect if not present'''
    @functools.wraps(route)
    def decorated_route(*args, **kwargs):
        '''Checks if uuid is in session, redirects to authenticate if not'''
        if 'uuid' not in session:
            APP.logger.info('No UUID, redirecting from {}'.format(request.url))
            return redirect(url_for('authenticate'))
        return route(*args, **kwargs)
    return decorated_route


def credentials_required(route):
    '''Wraps a route to require credentials and redirect if not present'''
    @functools.wraps(route)
    def decorated_route(*args, **kwargs):
        '''Checks if uuid is in session, redirects to authenticate if not'''
        if 'uuid' not in session:
            APP.logger.info('No UUID, redirecting from {}'.format(request.url))
            return redirect(url_for('authenticate'))
        user_uuid = session['uuid']
        if not authentication.get_facebook_access_token(user_uuid):
            APP.logger.info(
                'Facebook token missing, redirecting from {}'.format(
                    request.url))
            return redirect(authentication.get_facebook_authentication_uri(
                full_url('facebook')))
        if not authentication.get_google_credentials(user_uuid):
            APP.logger.info(
                'Google token missing, redirecting from {}'.format(
                    request.url))
            return redirect(authentication.get_google_authentication_uri(
                full_url('google')))
        return route(*args, **kwargs)
    return decorated_route


@APP.route('/logout')
def logout():
    '''Clears session'''
    APP.logger.info('Clearing UUID')
    session.clear()
    return redirect(url_for('home'))


@APP.route('/')
@credentials_required
def home():
    '''Home page'''
    return render_template('index.html', update_url=url_for('update'))


@APP.route('/authenticate')
def authenticate():
    '''Authenticates the user with Facebook and Google'''
    session['uuid'] = str(uuid.uuid4())
    APP.logger.info('UUID is {}'.format(session['uuid']))
    return redirect(
        authentication.get_facebook_authentication_uri(full_url('facebook')))


@APP.route('/facebook')
@uuid_required
def facebook():
    '''Gets the Facebook auth token and stores it in cookies'''
    authentication.save_facebook_access_token(
        session['uuid'],
        request.args.get('code'),
        full_url('facebook'))
    return redirect(
        authentication.get_google_authentication_uri(full_url('google')))


@APP.route('/google')
@uuid_required
def google():
    '''Saves Google credentials'''
    authentication.save_google_credentials(
        session['uuid'],
        request.args.get('code'),
        full_url('google'))
    return redirect(url_for('home'))


@APP.route('/update', methods=['POST'])
@credentials_required
def update():
    '''Uploads all new videos to YouTube'''
    return '<br>'.join(updates.update(
        session['uuid'],
        request.form['group_id'],
        request.form['playlist_id']))


def full_url(route):
    '''Returns an absolute URL using the host in the request'''
    parts = urllib.parse.urlparse(request.url)
    scheme = parts[0]
    netloc = parts[1]
    return urllib.parse.urlunparse(
        [scheme, netloc, url_for(route), None, None, None])
