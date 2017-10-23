"""
Import class
"""
from biredirect.dbservice import DBService  # noqa
from biredirect.settings import REDIS_URL, SECRET_KEY  # noqa

# Start shared database service
DB = DBService(REDIS_URL)
