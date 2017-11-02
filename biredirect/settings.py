"""
Application settings
"""
from os import environ

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
# Heroku variables
HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME")
REDIS_URL = environ.get("REDIS_URL")
SECRET_KEY = environ.get("SECRET_KEY")
# Auth0 variables
AUTH0_CALLBACK_URL = environ['AUTH0_CALLBACK_URL']
AUTH0_CLIENT_ID = environ['AUTH0_CLIENT_ID']
AUTH0_CLIENT_SECRET = environ['AUTH0_CLIENT_SECRET']
AUTH0_DOMAIN = environ['AUTH0_DOMAIN']
