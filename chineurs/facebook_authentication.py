"""Functions related to Facebook authentication"""
import urllib

import requests

from chineurs import settings


APP_ID = '1674357806183024'


def get_access_token(code, redirect_uri):
    """Exchanges a code for a Facebook user access token"""
    uri = ('https://graph.facebook.com/v2.8/oauth/access_token?'
           'client_id=%s&redirect_uri=%s&client_secret=%s&code=%s' % (
               APP_ID,
               urllib.parse.quote(redirect_uri),
               settings.APP_SECRET,
               code))
    return requests.get(uri).json()['access_token']
