"""
Shared fixtures
"""
import pytest
from redis import StrictRedis
from tests import mock
from boxsdk import OAuth2
from biredirect import redirector, settings, boxstores

@pytest.fixture
def oauth():
    mock_oauth = mock.Mock(spec=OAuth2)
    mock_oauth.get_authorization_url.return_value = ('http://auth_url', 'csrf_0123')
    return mock_oauth

@pytest.fixture
def box_redis_store(oauth):
    mock_box_redis_store = mock.Mock(spec=boxstores.BoxKeysStoreRedis)
    mock_box_redis_store.get_oauth.return_value = oauth
    return mock_box_redis_store

@pytest.fixture
def redisdb():
    mock_redisdb = mock.Mock(spec=StrictRedis)
    mock_redisdb.hget.return_value = 'csrf_0123'
    return mock_redisdb

@pytest.fixture
def webapp(redisdb, box_redis_store):
    flask_app = redirector.APP
    flask_app.debug = True
    redirector.BoxKeysStoreRedis = box_redis_store
    redirector.REDIS_DB = redisdb
    client = flask_app.test_client()

    return client
