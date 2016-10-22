'''Webpack resource management helpers'''
import json
import pkg_resources

from chineurs import app


def get_resources():
    '''Returns a map of webpack-managed resources'''
    if app.APP.debug:
        return {
            'js': ['http://localhost:8080/app.js'],
            'css': [],
        }
    else:
        webpack_assets = json.loads(pkg_resources.resource_string(
            'chineurs', 'frontend/webpack-assets.json').decode('utf-8'))
        return {
            'js': ['static/{}'.format(webpack_assets['main']['js'])],
            'css': ['static/{}'.format(webpack_assets['main']['css'])],
        }
