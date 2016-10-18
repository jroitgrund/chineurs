'''Flask app'''
import logging

from flask import Flask

from chineurs import settings

APP = Flask(__name__)
APP.secret_key = settings.SECRET_KEY
APP.debug = settings.DEBUG
APP.logger.setLevel(logging.INFO)
