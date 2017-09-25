"""
Tests for Redirector app
"""
import pytest

from biredirect.settings import (AUTH0_CALLBACK_URL, AUTH0_CLIENT_ID,
                                 AUTH0_CLIENT_SECRET, AUTH0_DOMAIN,
                                 HEROKU_APP_NAME)


def test_redirect_to_box(webapp):
    response = webapp.get('/api/redirect')

    assert response.status_code == 200
    assert response.data.decode() == 'a'


def test_redirect_to_box_success(webapp):
    response = webapp.get('/api/redirect?docID=abc')

    assert response.status_code == 302
    assert response.location == 'https://amadeus.box.com/shared/static/abc'


def test_redirect_to_onedrive(webapp):
    response = webapp.get('/api/redirect/onedrive')

    assert response.status_code == 302


def test_onedrive_success(webapp):
    response = webapp.get('/api/redirect/onedrive?filename=abc')

    assert response.status_code == 302
    assert response.location == 'https://myoffice.accenture.com/personal/c_sanchez_mateo_accenture_com/Documents/IFTTT/Gmail/abc'


@pytest.mark.parametrize("redirectTo, expectedUrl", [
    (None, "http://localhost/"),
    ("dashboard", "http://localhost/dashboard")
])
def test_callback_handling(webapp, get_token, token_instance, users, users_instance, redirectTo, expectedUrl):
    url = "/api/authcallback?code=auth0code"
    url = f'{url}&redirectto={redirectTo}' if redirectTo else url
    response = webapp.get(url)

    get_token.assert_called_once_with(AUTH0_DOMAIN)
    users.assert_called_once_with(AUTH0_DOMAIN)
    token_instance.authorization_code.assert_called_once_with(
        AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, 'auth0code', AUTH0_CALLBACK_URL)
    users_instance.userinfo.assert_called_once_with('at')
    assert response.status_code == 302
    assert response.location == expectedUrl


def test_logout(webapp):
    response = webapp.get('/logout')

    assert response.status_code == 302
    assert response.location == f'https://{AUTH0_DOMAIN}/v2/logout?returnTo=https://{HEROKU_APP_NAME}.herokuapp.com/&client_id={AUTH0_CLIENT_ID}'


def test_authenticate(webapp, box_redis_store, oauth, redisdb):
    response = webapp.get('/api/authenticate')

    box_redis_store.get_oauth.assert_called_once_with()
    oauth.get_authorization_url.assert_called_once_with(
        f'https://{HEROKU_APP_NAME}.herokuapp.com/api/boxauth')
    redisdb.hset.assert_called_once_with('box', 'csrf_token', 'csrf_0123')
    assert response.location == 'http://auth_url'


def test_box_auth(webapp, box_redis_store, redisdb, oauth):
    response = webapp.get('/api/boxauth?state=csrf_0123&code=auth_0123')

    redisdb.hget.assert_called_once_with('box', 'csrf_token')
    box_redis_store.get_oauth.assert_called_once_with()
    oauth.authenticate.assert_called_once_with('auth_0123')
    assert response.status_code == 200
    assert response.data.decode() == (
        'Authenticated. You can close this window.')


def test_box_auth_failure(webapp, redisdb):
    response = webapp.get('/api/boxauth?state=csrf_1234&code=auth_0123')
    redisdb.hget.assert_called_once_with('box', 'csrf_token')

    assert response.status_code == 200
    assert response.data.decode() == "Tokens don't match"
