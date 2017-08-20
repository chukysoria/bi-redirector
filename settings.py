"""
Application settings
"""
from os import environ

from dotenv import find_dotenv, load_dotenv
from redis import StrictRedis

load_dotenv(find_dotenv())

DOWNLOAD_PATH = environ.get('DOWNLOAD_PATH')
REPORT_SERVER = environ.get('REPORT_SERVER')
REPORT_USERNAME = environ.get('REPORT_USERNAME')
REPORT_PASSWORD = environ.get('REPORT_PASSWORD')
PORT = int(environ.get('PORT'))
BOX_CLIENT_SECRET = environ.get('BOX_CLIENT_SECRET')
BOX_CLIENT_ID = environ.get('BOX_CLIENT_ID')
BOX_DESTINATION_FOLDER = environ.get('BOX_DESTINATION_FOLDER')
FILE_LIST = environ.get('FILE_LIST')
REDIS_DB = StrictRedis.from_url(environ.get("REDIS_URL"), decode_responses=True)
HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME")
