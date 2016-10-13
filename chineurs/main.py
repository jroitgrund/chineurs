'''Entry point for chineurs server'''
import urllib

from flask import Flask, redirect, render_template, request, session, url_for

from chineurs import (
    authentication,
    settings,
    updates)


APP = Flask(__name__)
APP.secret_key = settings.SECRET_KEY
APP.debug = settings.DEBUG


@APP.route('/')
def home():
    if request.args.get('new'):
        session.clear()
    if 'facebook_access_token' in session and 'google_access_token' in session:
        return render_template('index.html', update_url=url_for('update'))
    else:
        return redirect(url_for('authenticate'))


@APP.route('/authenticate')
def authenticate():
    '''Authenticates the user with Facebook and Google'''
    uri = (
        'https://www.facebook.com/v2.8/dialog/oauth?'
        'client_id=%s&redirect_uri=%s' % (
            urllib.parse.quote(authentication.FACEBOOK_APP_ID),
            urllib.parse.quote(url_for('facebook'))))
    return redirect(uri)


@APP.route('/facebook')
def facebook():
    '''Gets the Facebook auth token and stores it in cookies'''
    session['facebook_access_token'] = (
            authentication.get_facebook_access_token(
                request.args.get('code'),
                urllib.parse.quote(url_for('facebook'))))
    uri = (
        'https://accounts.google.com/o/oauth2/v2/auth?'
        'scope=https://www.googleapis.com/auth/youtube&'
        'response_type=code&'
        'client_id={}&'
        'redirect_uri={}'.format(
            urllib.parse.quote(authentication.GOOGLE_APP_ID),
            urllib.parse.quote(url_for('google'))))
    return redirect(uri)


@APP.route('/google')
def google():
    '''Gets the Google auth token and stores it in cookies'''
    session['google_access_token'] = authentication.get_google_access_token(
        request.args.get('code'),
        urllib.parse.quote(url_for('google')))
    return redirect(url_for('home'))


@APP.route('/update', methods=['POST'])
def update():
    '''Uploads all new videos to YouTube'''
    return updates.update(
        session['facebook_access_token'],
        request.form['groupId'],
        session['google_access_token'],
        request.form['playlistId'])
