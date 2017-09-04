"""
Tests for BoxResponse app
"""
import pytest


def test_box_auth(webbox, oauth, appconfig):
    appconfig['csrf_token'] = 'csrf_0123'
    with pytest.raises(RuntimeError):
        response = webbox.get('/boxauth?state=csrf_0123&code=auth_0123')

        oauth.authenticate.assert_called_once_with('auth_0123')
        assert response.status_code == 200
        assert response.data.decode() == (
            'Authenticated. You can close this window.')


def test_box_auth_failure(webbox, appconfig):
    appconfig['csrf_token'] = 'csrf_0123'
    with pytest.raises(RuntimeError):
        response = webbox.get('/boxauth?state=csrf_1234&code=auth_0123')

        assert response.status_code == 200
        assert response.data.decode() == "Tokens don't match"
