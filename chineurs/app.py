'''Flask app'''
import logging

from flask import Flask

from chineurs import settings

APP = Flask(__name__)
APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
APP.secret_key = settings.SECRET_KEY


HANDLER = logging.StreamHandler()
HANDLER.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(module)s:%(lineno)d] %(levelname)s: %(message)s'))
APP.logger.handlers = [HANDLER]
