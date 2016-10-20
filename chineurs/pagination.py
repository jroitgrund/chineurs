'''Functions for pagination'''

import requests


def get_paginated_resource(  # pylint:disable=W0102
        url, get_next_page_url,
        get_keep_fetching=lambda page: True,
        headers={}):
    '''Gets a paginated resource given how to get the next page
       and when to keep fetching'''
    while url:
        if headers:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)
        response.raise_for_status()
        json = response.json()
        yield json
        url = get_keep_fetching(json) and get_next_page_url(json)
