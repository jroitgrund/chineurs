'''Read settings from .env or environment variables'''

import os
from os.path import join, dirname
from dotenv import load_dotenv

DOTENV_PATH = join(dirname(__file__), '..', '.env')
load_dotenv(DOTENV_PATH)

DATA_DIRECTORY = os.environ.get('DATA_DIRECTORY')
DEBUG = bool(os.environ.get('DEBUG'))
FACEBOOK_SECRET = os.environ.get('FACEBOOK_SECRET')
GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET')
SECRET_KEY = os.environ.get('SECRET_KEY')
