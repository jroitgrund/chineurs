'''Read settings from .env or environment variables'''

import os
from os.path import join, dirname
from dotenv import load_dotenv

DOTENV_PATH = join(dirname(__file__), '..', '.env')
load_dotenv(DOTENV_PATH)

CELERY_BROKER = os.environ.get('CELERY_BROKER')
FACEBOOK_SECRET = os.environ.get('FACEBOOK_SECRET')
GOOGLE_SECRET = os.environ.get('GOOGLE_SECRET')
TEST_POSTGRES_DB = os.environ.get('TEST_POSTGRES_DB')
TEST_POSTGRES_HOST = os.environ.get('TEST_POSTGRES_HOST')
TEST_POSTGRES_USER = os.environ.get('TEST_POSTGRES_USER')
SECRET_KEY = os.environ.get('SECRET_KEY')
