'''Functions related to Facebook authentication'''
import urllib

import requests

from chineurs import settings


FACEBOOK_APP_ID = '1674357806183024'
GOOGLE_APP_ID = (
        '523747931727-husefd5edn8amees69gojq2scpaddbm2'
        '.apps.googleusercontent.com')


def get_facebook_access_token(code, redirect_uri):
    '''Exchanges a code for a Facebook user access token'''
    uri = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'client_id=%s&redirect_uri=%s&client_secret=%s&code=%s' % (
               urllib.parse.quote(FACEBOOK_APP_ID),
               urllib.parse.quote(redirect_uri),
               urllib.parse.quote(settings.FACEBOOK_SECRET),
               code))
    return requests.get(uri).json()['access_token']


def get_google_access_token(code, redirect_uri):
    '''Exchanges a code for a Google user access token'''
    uri = ('https://www.googleapis.com/oauth2/v4/token?'
           'grant_type=authorization_code&'
           'client_id=%s&redirect_uri=%s&client_secret=%s&code=%s' % (
               urllib.parse.quote(GOOGLE_APP_ID),
               urllib.parse.quote(redirect_uri),
               urllib.parse.quote(settings.GOOGLE_SECRET),
               code))
    return requests.get(uri).json()['access_token']
