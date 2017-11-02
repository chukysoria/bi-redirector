"""
Box Keys store for Heroku/Redis
"""
from boxsdk import OAuth2

from biredirect import DB
from biredirect.utils import get_config


class BoxKeysStoreRedis:
    """
    Read/save tokens from Heroku Redis
    """

    def __init__(self, client_id=None, client_secret=None):
        if client_id:
            self._client_id = client_id
        else:
            self._client_id = get_config('BOX_CLIENT_ID')

        if client_secret:
            self._client_secret = client_secret
        else:
            self._client_secret = get_config('BOX_CLIENT_SECRET')

    def get_oauth(self):
        """
        Creates an Oauth object

        :return:
            oauth object.
        :rtype:
            :class:`boxsdk.Oauth2`
        """
        box_token = DB.get_hash_keys('box')
        if 'accessToken' in box_token.keys():
            oauth = OAuth2(
                client_id=self._client_id,
                client_secret=self._client_secret,
                store_tokens=self._store_tokens,
                access_token=box_token['accessToken'],
                refresh_token=box_token['refreshToken']
            )
        else:
            oauth = OAuth2(
                client_id=self._client_id,
                client_secret=self._client_secret,
                store_tokens=self._store_tokens
            )
        return oauth

    @classmethod
    def _store_tokens(cls, access_token, refresh_token):
        """
        Store token values in redis.
        :param access_token:
            Box Access token
        :param refresh_token:
            Box Refresh token
        """
        data = {}
        data['accessToken'] = access_token
        data['refreshToken'] = refresh_token
        DB.set_hash_keys('box', data)
