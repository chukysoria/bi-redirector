"""
Tests for Boxstores
"""
from unittest import mock

from biredirect import boxstores, settings


@mock.patch("biredirect.boxstores.REDIS_DB")
def test_get_oauth(redisdb):
    redisdb.hgetall.return_value = {'accessToken': 'a', 'refreshToken': 'r'}
    oauth = boxstores.BoxKeysStoreRedis.get_oauth()

    redisdb.hgetall.assert_called_once_with('box')
    assert oauth._client_id == settings.BOX_CLIENT_ID
    assert oauth._client_secret == settings.BOX_CLIENT_SECRET
    assert oauth._store_tokens_callback == (
        boxstores.BoxKeysStoreRedis._store_tokens)
    assert oauth._refresh_token == 'r'
    assert oauth.access_token == 'a'


@mock.patch("biredirect.boxstores.REDIS_DB")
def test_get_oauth_new(redisdb):
    redisdb.hgetall.return_value = {}
    oauth = boxstores.BoxKeysStoreRedis.get_oauth()

    redisdb.hgetall.assert_called_once_with('box')
    assert oauth._client_id == settings.BOX_CLIENT_ID
    assert oauth._client_secret == settings.BOX_CLIENT_SECRET
    assert oauth._store_tokens_callback == (
        boxstores.BoxKeysStoreRedis._store_tokens)
    assert oauth._refresh_token is None
    assert oauth.access_token is None


@mock.patch("biredirect.boxstores.REDIS_DB")
def test_store_tokens(redisdb):
    boxstores.BoxKeysStoreRedis._store_tokens('a', 'r')

    redisdb.hmset.assert_called_once_with('box',
                                          {'accessToken': 'a',
                                           'refreshToken': 'r'})
