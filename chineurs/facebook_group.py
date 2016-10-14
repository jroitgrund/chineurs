'''Functions related to a Facebook group's feed'''
from datetime import datetime
from itertools import chain
import re
import requests

FACEBOOK_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
YOUTUBE_URL_REGEX = re.compile('youtube.com')


class ExpiredFacebookToken(Exception):
    '''Raised when the facebook token is expired'''

    def __init__(self):
        Exception.__init__(self)


def get_youtube_links(
        group_id, access_token, earliest_timestamp):
    '''Returns a list of all YouTube links in a group's feed'''
    earliest_datetime = get_datetime(earliest_timestamp)
    uri = ('https://graph.facebook.com/v2.8/%s/feed?access_token=%s' %
           (group_id, access_token))
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
        posts.extend(chain.from_iterable(
            find_youtube_urls(post['message']) for post
            in new_posts
            if 'message' in post))
        if 'paging' in posts_response and (
                len(new_posts) == len(posts_response['data'])):
            uri = posts_response['paging']['next']
        else:
            uri = None
    return posts


def get_datetime(facebook_timestamp):
    '''Parses a facebook format timestamp into a datetime'''
    return datetime.strptime(facebook_timestamp, FACEBOOK_TIMESTAMP_FORMAT)


def find_youtube_urls(post):
    '''Yields all the YouTube URLs in a wall post as an iterator'''
    return (word for word in post.split(' ') if YOUTUBE_URL_REGEX.search(word))
