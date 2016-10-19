'''Functions related to a Facebook group's feed'''
from collections import OrderedDict
from datetime import datetime
from itertools import chain
import re
import requests

from chineurs import storage

FACEBOOK_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
VIDEO_ID_REGEX = re.compile(r'/watch\?v=([^&#\s]*)')


class ExpiredFacebookToken(Exception):
    '''Raised when the facebook token is expired'''

    def __init__(self):
        Exception.__init__(self)


def get_facebook_id(access_token):
    '''Return the facebook id'''
    return requests.get(
        'https://graph.facebook.com/v2.8/me?access_token={}'.format(
            access_token)).json()['id']


def save_groups(user_id):
    '''Return list of matching Facebook groups'''
    # pylint:disable=E1120
    uri = ('https://graph.facebook.com/v2.8/me/groups?'
           'limit=1000&access_token={}'.format(
               storage.get_user_by_id(user_id)['fb_access_token']))
    groups = []
    while uri:
        try:
            response = requests.get(uri)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ExpiredFacebookToken()
        json = response.json()
        groups.extend(
            {key: group[key] for key in ['id', 'name']}
            for group in json['data'])
        uri = json.get('paging', {}).get('next', None)
    storage.save_facebook_groups(user_id, groups)


def search_for_group(user_id, query):
    '''Text search for groups'''
    # pylint:disable=E1120
    return [group for group in storage.get_facebook_groups(user_id)
            if query.lower() in group['name'].lower()]


def get_youtube_links(
        group_id, access_token, earliest_datetime):
    '''Returns a list of all YouTube links in a group's feed'''
    uri = ('https://graph.facebook.com/v2.8/%s/feed?access_token=%s&'
           'fields=id,message,link,updated_time&'
           'limit=1000' % (group_id, access_token))
    posts = []
    while uri:
        try:
            response = requests.get(uri)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise ExpiredFacebookToken()
        posts_response = response.json()
        new_posts = posts_response['data']
        new_posts = [
            post for post in posts_response['data'] if
            get_datetime(post['updated_time']) > earliest_datetime]
        posts.extend(new_posts)
        if len(new_posts) == len(posts_response['data']):
            uri = posts_response.get('paging', {}).get('next', None)
        else:
            uri = None
    video_ids = chain.from_iterable(
        find_youtube_ids(
            '{} {}'.format(
                post.get('message', ''), post.get('link', '')))
        for post in posts)
    return reversed(OrderedDict.fromkeys(video_ids).keys())


def get_datetime(facebook_timestamp):
    '''Parses a facebook format timestamp into a datetime'''
    return datetime.strptime(facebook_timestamp, FACEBOOK_TIMESTAMP_FORMAT)


def find_youtube_ids(post):
    '''Yields all the YouTube ids in a wall post as an iterator'''
    return (match.group(1) for match in VIDEO_ID_REGEX.finditer(post))
