"""Read settings from .env or environment variables"""

import os
from os.path import join, dirname
from dotenv import load_dotenv

DOTENV_PATH = join(dirname(__file__), '.env')
load_dotenv(DOTENV_PATH)

APP_SECRET = os.environ.get('APP_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI')
