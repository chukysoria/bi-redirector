"""
Shared fixtures
"""
import json
from unittest import mock

from auth0.v3.authentication import GetToken, Users
from boxsdk import OAuth2
import pytest
from redis import StrictRedis

from biredirect import DBService, boxstores, redirector
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
    mock_box_redis_store.return_value = mock_box_redis_store
    return mock_box_redis_store


@pytest.fixture
def token_instance():
    mock_token = mock.Mock(spec=GetToken)
    mock_token.authorization_code.return_value = {'access_token': 'at'}
    return mock_token


@pytest.fixture
def get_token(token_instance):
    mock_get_token = mock.Mock(spec=GetToken)
    mock_get_token.return_value = token_instance
    return mock_get_token


@pytest.fixture
def users_instance():
    mock_users_instace = mock.Mock(spec=Users)
    mock_users_instace.userinfo.return_value = \
        '{"sub":"auth0|59","name":"xx@gmail.com","nickname":"xx",'\
        '"picture":"https://s.gravatar.com/avatar/x","updated_at":"sometime"}'
    return mock_users_instace


@pytest.fixture
def users(users_instance):
    mock_users = mock.Mock(spec=Users)
    mock_users.return_value = users_instance
    return mock_users


@pytest.fixture
def get_config(config_name):
    return f'value_{config_name}'


@pytest.fixture
def redisdb():
    mock_redisdb = mock.Mock(spec=StrictRedis)
    mock_redisdb.hget.return_value = 'csrf_0123'
    return mock_redisdb


@pytest.fixture
def dbservice():
    mock_dbservice = mock.Mock(spec=DBService)
    mock_dbservice.get_crsf_token.return_value = 'csrf_0123'
    mock_dbservice.insert_config = insert_config
    mock_dbservice.get_config = retrieve_config
    mock_dbservice.update_config = update_config
    mock_dbservice.delete_config = retrieve_config
    mock_dbservice.config_exists.return_value = False
    mock_dbservice.get_configs.return_value = (
        [retrieve_config('a'), retrieve_config('b')])
    return mock_dbservice


def insert_config(data):
    try:
        if data['name'] and data['value']:
            return data
    except:
        return None


def retrieve_config(config_name):
    if config_name != 'fail':
        return {'name': config_name, 'value': 'v', 'secure': False}
    return None


def update_config(config_name, data):
    config = retrieve_config(config_name)
    if config:
        config['name'] = data['name']
        config['value'] = data['value']
        return config
    return None


@pytest.fixture
def webapp(dbservice, box_redis_store, get_token, users):
    flask_app = redirector.APP
    flask_app.debug = True
    flask_app.config['TESTING'] = True
    redirector.BoxKeysStoreRedis = box_redis_store
    redirector.DB = dbservice
    redirector.GetToken = get_token
    redirector.Users = users
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
