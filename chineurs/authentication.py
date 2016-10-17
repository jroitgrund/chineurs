'''Functions related to Facebook authentication'''
import os
import urllib

import oauth2client
from oauth2client.client import OAuth2WebServerFlow
import oauth2client.file
import requests

from chineurs import settings
from chineurs.storage import Storage


FACEBOOK_APP_ID = '1674357806183024'
GOOGLE_APP_ID = (
    '523747931727-husefd5edn8amees69gojq2scpaddbm2'
    '.apps.googleusercontent.com')


def get_facebook_authentication_uri(redirect_uri):
    '''Gets the URI to redirect the user to for Facebook authentication'''
    return (
        'https://www.facebook.com/v2.8/dialog/oauth?'
        'client_id={}&redirect_uri={}'.format(
            urllib.parse.quote(FACEBOOK_APP_ID),
            urllib.parse.quote(redirect_uri)))


def save_facebook_access_token(uuid, code, redirect_uri):
    '''Exchange a code for a Facebook user access token and save it'''
    storage = Storage(uuid)
    uri = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'client_id={}&redirect_uri={}&client_secret={}&code={}'.format(
               urllib.parse.quote(FACEBOOK_APP_ID),
               urllib.parse.quote(redirect_uri),
               urllib.parse.quote(settings.FACEBOOK_SECRET),
               code))
    storage.set('facebook-token', requests.get(uri).json()['access_token'])


def get_facebook_access_token(uuid):
    '''Retrieves a Facebook access token'''
    return Storage(uuid).get('facebook-token')


def get_google_authentication_uri(redirect_uri):
    '''Return an object for the Google authentication flow'''
    return OAuth2WebServerFlow(
        GOOGLE_APP_ID,
        settings.GOOGLE_SECRET,
        scope=[
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube'],
        redirect_uri=redirect_uri).step1_get_authorize_url()


def save_google_credentials(uuid, code, redirect_uri):
    '''Save google credentials to disk if they don't exist already'''
    storage = get_google_storage(uuid)
    if not storage.get():
        storage.put(OAuth2WebServerFlow(
            GOOGLE_APP_ID,
            settings.GOOGLE_SECRET,
            scope=[
                'https://www.googleapis.com/auth/youtube.force-ssl',
                'https://www.googleapis.com/auth/youtube'],
            redirect_uri=redirect_uri).step2_exchange(code))


def get_google_credentials(uuid):
    '''Get google credentials from disk'''
    return get_google_storage(uuid).get()


def get_google_storage(uuid):
    '''Get the Google credentials file storage'''
    return oauth2client.file.Storage(os.path.join(
        Storage(uuid).directory,
        'google-credentials'))
