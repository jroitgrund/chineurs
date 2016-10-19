'''Functions related to Facebook authentication'''
import urllib

from oauth2client.client import OAuth2WebServerFlow
import requests

from chineurs import settings, storage


FACEBOOK_APP_ID = '1674357806183024'
GOOGLE_APP_ID = (
    '523747931727-husefd5edn8amees69gojq2scpaddbm2'
    '.apps.googleusercontent.com')

# pylint:disable=E1120


def get_facebook_authentication_uri(redirect_uri):
    '''Gets the URI to redirect the user to for Facebook authentication'''
    return (
        'https://www.facebook.com/v2.8/dialog/oauth?'
        'client_id={}&redirect_uri={}'.format(
            urllib.parse.quote(FACEBOOK_APP_ID),
            urllib.parse.quote(redirect_uri)))


def save_facebook_access_token(code, redirect_uri):
    '''Exchange a code for a Facebook user access token and save it'''
    uri = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'client_id={}&redirect_uri={}&client_secret={}&code={}'.format(
               urllib.parse.quote(FACEBOOK_APP_ID),
               urllib.parse.quote(redirect_uri),
               urllib.parse.quote(settings.FACEBOOK_SECRET),
               code))
    access_token = requests.get(uri).json()['access_token']
    facebook_id = requests.get(
        'https://graph.facebook.com/v2.8/me?'
        'access_token={}'.format(access_token)).json()['id']
    return storage.get_user_id(facebook_id, access_token)


def get_google_authentication_uri(redirect_uri):
    '''Return an object for the Google authentication flow'''
    return OAuth2WebServerFlow(
        GOOGLE_APP_ID,
        settings.GOOGLE_SECRET,
        scope=[
            'https://www.googleapis.com/auth/youtubepartner',
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube'],
        redirect_uri=redirect_uri).step1_get_authorize_url()


def save_google_credentials(user_id, code, redirect_uri):
    '''Save google credentials to disk if they don't exist already'''
    user = storage.get_user_by_id(user_id)
    if not user['google_credentials']:
        storage.set_user_google_credentials(user_id, OAuth2WebServerFlow(
            GOOGLE_APP_ID,
            settings.GOOGLE_SECRET,
            scope=[
                'https://www.googleapis.com/auth/youtubepartner',
                'https://www.googleapis.com/auth/youtube.force-ssl',
                'https://www.googleapis.com/auth/youtube'],
            redirect_uri=redirect_uri).step2_exchange(code))
