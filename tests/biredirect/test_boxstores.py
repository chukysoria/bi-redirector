"""
Tests for Boxstores
"""
from unittest import mock

from biredirect.boxstores import BoxKeysStoreRedis


@mock.patch("biredirect.boxstores.get_config")
@mock.patch("biredirect.boxstores.DB")
def test_get_oauth(redisdb, get_config):
    redisdb.get_hash_keys.return_value = {'accessToken': 'a',
                                          'refreshToken': 'r'}
    box_keys_store = BoxKeysStoreRedis()
    oauth = box_keys_store.get_oauth()

    redisdb.get_hash_keys.assert_called_once_with('box')
    assert oauth._client_id == get_config('BOX_CLIENT_ID')
    assert oauth._client_secret == get_config('BOX_CLIENT_SECRET')
    assert oauth._store_tokens_callback == (
        box_keys_store._store_tokens)
    assert oauth._refresh_token == 'r'
    assert oauth.access_token == 'a'


@mock.patch("biredirect.boxstores.DB")
def test_get_oauth_params(redisdb):
    redisdb.get_hash_keys.return_value = {'accessToken': 'a',
                                          'refreshToken': 'r'}
    box_keys_store = BoxKeysStoreRedis('a', 'b')
    oauth = box_keys_store.get_oauth()

    redisdb.get_hash_keys.assert_called_once_with('box')
    assert oauth._client_id == 'a'
    assert oauth._client_secret == 'b'
    assert oauth._store_tokens_callback == (
        box_keys_store._store_tokens)
    assert oauth._refresh_token == 'r'
    assert oauth.access_token == 'a'


@mock.patch("biredirect.boxstores.DB")
def test_get_oauth_new(redisdb):
    redisdb.get_hash_keys.return_value = {}
    box_keys_store = BoxKeysStoreRedis('a', 'b')
    oauth = box_keys_store.get_oauth()

    redisdb.get_hash_keys.assert_called_once_with('box')
    assert oauth._client_id == 'a'
    assert oauth._client_secret == 'b'
    assert oauth._store_tokens_callback == (
        box_keys_store._store_tokens)
    assert oauth._refresh_token is None
    assert oauth.access_token is None


@mock.patch("biredirect.boxstores.DB")
def test_store_tokens(redisdb):
    box_keys_store = BoxKeysStoreRedis('a', 'b')
    box_keys_store._store_tokens('a', 'r')

    redisdb.set_hash_keys.assert_called_once_with(
        'box', {'accessToken': 'a', 'refreshToken': 'r'})
