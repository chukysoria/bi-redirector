"""
Tests for Redirector app
"""
import pytest

from biredirect.settings import (API_TOKEN, AUTH0_CALLBACK_URL,
                                 AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET,
                                 AUTH0_DOMAIN, HEROKU_APP_NAME)


def test_redirect_to_box(webapp):
    response = webapp.get(f'/api/redirect?Authorization={API_TOKEN}')

    assert response.status_code == 200
    assert response.data.decode() == 'a'


def test_redirect_to_box_success(webapp):
    response = webapp.get(
        f'/api/redirect?docID=abc&Authorization={API_TOKEN}')

    assert response.status_code == 503
    # assert response.location == 'https://amadeus.box.com/shared/static/abc'


@pytest.mark.parametrize("redirect_to, expected_url", [
    (None, "http://localhost/"),
    ("dashboard", "http://localhost/dashboard")
])
def test_callback_handling(webapp, get_token, token_instance, users,
                           users_instance, redirect_to, expected_url):
    url = "/api/authcallback?code=auth0code"
    url = f'{url}&redirectto={redirect_to}' if redirect_to else url
    response = webapp.get(url)

    get_token.assert_called_once_with(AUTH0_DOMAIN)
    users.assert_called_once_with(AUTH0_DOMAIN)
    token_instance.authorization_code.assert_called_once_with(
        AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, 'auth0code', AUTH0_CALLBACK_URL)
    users_instance.userinfo.assert_called_once_with('at')
    assert response.status_code == 302
    assert response.location == expected_url


def test_callback_handling_error(webapp):
    url = "/api/authcallback?error=a&error_description=errormsg"
    response = webapp.get(url)

    assert response.status_code == 401
    assert 'errormsg' in response.data.decode()


def test_logout(webapp):
    response = webapp.get('/logout')
    return_to = f'https://{HEROKU_APP_NAME}.herokuapp.com/'

    assert response.status_code == 302
    assert response.location == f'https://{AUTH0_DOMAIN}/v2/logout?'\
                                f'returnTo={return_to}&'\
                                f'client_id={AUTH0_CLIENT_ID}'


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
