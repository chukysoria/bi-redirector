"""
Tests for Redirector app
"""
from biredirect.settings import HEROKU_APP_NAME


def test_redirect_to_box(webapp):
    response = webapp.get('/redirect')

    assert response.status_code == 200
    assert response.data.decode() == 'a'


def test_redirect_to_box_success(webapp):
    response = webapp.get('/redirect?docID=abc')

    assert response.status_code == 302
    assert response.location == 'https://amadeus.box.com/shared/static/abc'


def test_authenticate(webapp, box_redis_store, oauth, redisdb):
    response = webapp.get('/authenticate')

    box_redis_store.get_oauth.assert_called_once_with()
    oauth.get_authorization_url.assert_called_once_with(
        f'https://{HEROKU_APP_NAME}.herokuapp.com/boxauth')
    redisdb.hset.assert_called_once_with('box', 'csrf_token', 'csrf_0123')
    assert response.location == 'http://auth_url'


def test_box_auth(webapp, box_redis_store, redisdb, oauth):
    response = webapp.get('/boxauth?state=csrf_0123&code=auth_0123')

    redisdb.hget.assert_called_once_with('box', 'csrf_token')
    box_redis_store.get_oauth.assert_called_once_with()
    oauth.authenticate.assert_called_once_with('auth_0123')
    assert response.status_code == 200
    assert response.data.decode() == (
        'Authenticated. You can close this window.')


def test_box_auth_failure(webapp, redisdb):
    response = webapp.get('/boxauth?state=csrf_1234&code=auth_0123')
    redisdb.hget.assert_called_once_with('box', 'csrf_token')

    assert response.status_code == 200
    assert response.data.decode() == "Tokens don't match"
