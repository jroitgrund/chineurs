'''Functions related to a Facebook group's feed'''
from collections import OrderedDict
from datetime import datetime
from itertools import chain
import re
import requests

from chineurs import authentication, pagination

FACEBOOK_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
VIDEO_ID_REGEX = re.compile(r'/watch\?v=([^&#\s]*)')


def get_facebook_id(access_token):
    '''Return the facebook id'''
    return requests.get(
        'https://graph.facebook.com/v2.8/me?access_token={}'.format(
            access_token)).json()['id']


def get_pages(uri, get_keep_fetching=lambda page: True):
    '''Return all pages for this request'''
    def get_next_page_url(json):
        '''Returns the next page URL'''
        return json.get('paging', {}).get('next', None)
    try:
        return list(pagination.get_paginated_resource(
            uri, get_next_page_url, get_keep_fetching))
    except requests.exceptions.HTTPError:
        raise authentication.AuthExpired


def get_groups(access_token):
    '''Return list of matching Facebook groups'''
    pages = get_pages(
        'https://graph.facebook.com/v2.8/me/groups?'
        'limit=1000&access_token={}'.format(access_token))
    return sorted(
        [{key: group[key] for key in ['id', 'name']}
         for group in
         chain.from_iterable(page['data'] for page in pages)],
        key=lambda group: group['name'])


def get_youtube_links(
        group_id, access_token, earliest_datetime):
    '''Returns a list of all YouTube links in a group's feed'''
    def valid_post(post):
        '''Checks if a post is too early'''
        return get_datetime(post['updated_time']) > earliest_datetime
    pages = get_pages(
        'https://graph.facebook.com/v2.8/%s/feed?access_token=%s&'
        'fields=id,message,link,updated_time&'
        'limit=1000' % (group_id, access_token),
        lambda page: (
            len(page['data']) > 0 and
            valid_post(page['data'][-1])))
    posts = chain.from_iterable(page['data'] for page in pages)
    video_ids = chain.from_iterable(
        find_youtube_ids(
            '{} {}'.format(
                post.get('message', ''), post.get('link', '')))
        for post in posts if valid_post(post))
    return reversed(OrderedDict.fromkeys(video_ids).keys())


def get_datetime(facebook_timestamp):
    '''Parses a facebook format timestamp into a datetime'''
    return datetime.strptime(facebook_timestamp, FACEBOOK_TIMESTAMP_FORMAT)


def find_youtube_ids(post):
    '''Yields all the YouTube ids in a wall post as an iterator'''
    return (match.group(1) for match in VIDEO_ID_REGEX.finditer(post))
