"""
Application settings
"""
from os import environ

from dotenv import find_dotenv, load_dotenv
from redis import StrictRedis

load_dotenv(find_dotenv())
# Auth0 variables
AUTH0_CALLBACK_URL = environ['AUTH0_CALLBACK_URL']
AUTH0_CLIENT_ID = environ['AUTH0_CLIENT_ID']
AUTH0_CLIENT_SECRET = environ['AUTH0_CLIENT_SECRET']
AUTH0_DOMAIN = environ['AUTH0_DOMAIN']

# Box variables
BOX_CLIENT_ID = environ.get('BOX_CLIENT_ID')
BOX_CLIENT_SECRET = environ.get('BOX_CLIENT_SECRET')

# Heroku variables
HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME")
REDIS_URL = environ.get("REDIS_URL")
REDIS_DB = StrictRedis.from_url(environ.get("REDIS_URL"),
                                decode_responses=True)
PORT = int(environ.get('PORT'))
DOWNLOAD_PATH = environ.get('DOWNLOAD_PATH')

# Report variables
REPORT_SERVER = environ.get('REPORT_SERVER')
REPORT_USERNAME = environ.get('REPORT_USERNAME')
REPORT_PASSWORD = environ.get('REPORT_PASSWORD')

# Job variables
BOX_DESTINATION_FOLDER = environ.get('BOX_DESTINATION_FOLDER')
FILE_LIST = environ.get('FILE_LIST')
JOB_SNITCH = environ.get("JOB_SNITCH")
