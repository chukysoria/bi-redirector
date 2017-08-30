"""
Shared fixtures
"""
import json
from unittest import mock

from boxsdk import OAuth2
import pytest
from redis import StrictRedis

from biredirect import boxstores, redirector
from boxsync import boxresponse, boxsync


@pytest.fixture
def oauth():
    mock_oauth = mock.Mock(spec=OAuth2)
    mock_oauth.get_authorization_url.return_value = ('http://auth_url',
                                                     'csrf_0123')
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
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def appboxresponse(oauth):
    flask_app = boxresponse.FLASK_APP
    flask_app.debug = True
    flask_app.config['oauth'] = oauth
    return flask_app


@pytest.fixture
def appconfig(appboxresponse):
    return appboxresponse.config


@pytest.fixture
def webbox(appboxresponse):
    with appboxresponse.test_client() as client:
        yield client


@pytest.fixture
def json_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp('data').join('keys.json')
    data = {}
    data['clientID'] = 'cid'
    data['clientSecret'] = 'cs'
    data['accessToken'] = 'at'
    data['refreshToken'] = 'rt'
    with open(fn, 'w') as outfile:
        json.dump(data, outfile)
    return fn


@pytest.fixture
def box_ks(json_file):
    ks = boxsync.BoxKeysStoreFile(str(json_file))
    return ks
