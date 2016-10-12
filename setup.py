"""Setup file for chineurs"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

CONFIG = {
    'description': (
        'Grabs YouTube URLs from Facebook groups and '
        'makes playlists out of them'),
    'author': 'Jonathan Roitgrund',
    'url': 'https://github.com/jroitgrund/chineurs',
    'author_email': 'jroitgrund@gmail.com',
    'version': '0.1',
    'install_requires': ['flask', 'requests', 'python-dotenv', 'pytz', 'gunicorn'],
    'packages': ['chineurs'],
    'package_data': {
        'chineurs': ['tepmlates']
    },
    'scripts': [],
    'name': 'chineurs'
}

setup(**CONFIG)