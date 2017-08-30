"""
Tests for Boxsync app
"""
import pytest

from boxsync.boxsync import BoxAuthenticateInteractive, BoxKeysStoreFile


class TestBoxKeysStoreFile:

    @pytest.mark.parametrize("filename,expected", [
        (None, 'keys.json'),
        ("otherfile.json", "otherfile.json")
    ])
    def test_creation(self, filename, expected):
        if filename is None:
            ks = BoxKeysStoreFile()
        else:
            ks = BoxKeysStoreFile(filename)

        assert ks.keys_path == expected

    def test_get_oauth(self, box_ks):
        oauth = box_ks.get_oauth()

        assert oauth._client_id == 'cid'
        assert oauth._client_secret == 'cs'
        assert oauth.access_token == 'at'
        assert oauth._refresh_token == 'rt'
        assert oauth._store_tokens_callback == box_ks._store_tokens

    def test_store_tokens(self, box_ks):
        box_ks._store_tokens('new at', 'new rt')
        data = box_ks._read_token()

        assert data['clientID'] == 'cid'
        assert data['clientSecret'] == 'cs'
        assert data['accessToken'] == 'new at'
        assert data['refreshToken'] == 'new rt'


class TestBoxAuthenticateInteractive:

    def test_creation(self):
        ba = BoxAuthenticateInteractive()
        assert ba.server_hostname == 'localhost'
        assert ba.server_port == '5000'

    def test_creation_with_values(self):
        ba = BoxAuthenticateInteractive('abc', '4563')
        assert ba.server_hostname == 'abc'
        assert ba.server_port == '4563'
