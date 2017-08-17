# settings.py
from os import environ
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DOWNLOAD_PATH = environ.get('DOWNLOAD_PATH')
REPORT_SERVER = environ.get('REPORT_SERVER')
REPORT_USERNAME = environ.get('REPORT_USERNAME')
REPORT_PASSWORD = environ.get('REPORT_PASSWORD')
PORT = int(environ.get('PORT'))
