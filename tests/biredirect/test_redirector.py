"""
Tests for Redirector app
"""
import json
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


def test_create_config(webapp):
    response = webapp.post('/api/configs',
                           data=json.dumps({'name': 'n', 'value': 'v'}),
                           content_type='application/json')

    assert response.status_code == 201
    assert json.loads(response.data.decode()) == (
        {'data': {'name': 'N', 'value': 'v'}})


def test_create_config_failed(webapp):
    response = webapp.post('/api/configs',
                           data=json.dumps({'name': 'n'}),
                           content_type='application/json')

    assert response.status_code == 404
    assert json.loads(response.data.decode()) == (
        {'error': "Config don't created"})


def test_retrive_configs(webapp):
    response = webapp.get('/api/configs')

    assert response.status_code == 200
    assert json.loads(response.data.decode()) == {'data': [
        {'name': 'a', 'value': 'v'},
        {'name': 'b', 'value': 'v'}]}


@pytest.mark.parametrize("config_name, result", [
    ('a', {'data': {'name': 'a', 'value': 'v'}}),
    ('b', {'data': {'name': 'b', 'value': 'v'}}),
    ('fail', {"error": "name doesn't exist"})
])
def test_retrive_config(webapp, config_name, result):
    response = webapp.get(f'/api/configs/{config_name}')

    assert json.loads(response.data.decode()) == result


@pytest.mark.parametrize("config_name, result", [
    ('a', {'data': {'name': 'a', 'value': 'e'}}),
    ('b', {'data': {'name': 'b', 'value': 'e'}}),
    ('fail', {"error": "Not updated"})
])
def test_update_config(webapp, config_name, result):
    response = webapp.put(f'/api/configs/{config_name}',
                          data=json.dumps({'name': config_name, 'value': 'e'}),
                          content_type='application/json')

    assert json.loads(response.data.decode()) == result


@pytest.mark.parametrize("config_name, result", [
    ('a', {'result': 'success'}),
    ('b', {'result': 'success'}),
    ('fail', {"error": "Not deleted"})
])
def test_delete_config(webapp,  config_name, result):
    response = webapp.delete(f'/api/configs/{config_name}')

    assert json.loads(response.data.decode()) == result


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


def test_authenticate(webapp, box_redis_store, oauth, dbservice):
    response = webapp.get('/api/box/authenticate')

    box_redis_store.get_oauth.assert_called_once_with()
    oauth.get_authorization_url.assert_called_once_with(
        f'https://{HEROKU_APP_NAME}.herokuapp.com/api/box/callback')
    dbservice.set_crsf_token.assert_called_once_with('csrf_0123')
    assert response.location == 'http://auth_url'


def test_boxauth(webapp, box_redis_store, oauth):
    response = webapp.get('/api/box/callback?state=csrf_0123&code=auth_0123')

    box_redis_store.get_oauth.assert_called_once_with()
    oauth.authenticate.assert_called_once_with('auth_0123')
    assert response.status_code == 200
    assert response.data.decode() == (
        'Authenticated. You can close this window.')


def test_boxauth_failure(webapp):
    response = webapp.get('/api/box/callback?state=csrf_1234&code=auth_0123')

    assert response.status_code == 200
    assert response.data.decode() == "Tokens don't match"
