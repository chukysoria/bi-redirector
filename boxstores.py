"""
Box Keys store for Heroku/Redis
"""
from boxsdk import OAuth2

from settings import BOX_CLIENT_ID, BOX_CLIENT_SECRET, REDIS_DB


class BoxKeysStoreRedis:
    """
    Read/save tokens from Heroku Redis
    """
    @classmethod
    def get_oauth(cls):
        """
        Creates an Oauth object

        :return:
            oauth object.
        :rtype:
            :class:`boxsdk.Oauth2`
        """
        box_token = REDIS_DB.hgetall('box')
        oauth = OAuth2(
            client_id=BOX_CLIENT_ID,
            client_secret=BOX_CLIENT_SECRET,
            store_tokens=cls._store_tokens,
            access_token=box_token['accessToken'],
            refresh_token=box_token['refreshToken']
        )        
        return oauth

    @classmethod
    def _store_tokens(cls, access_token, refresh_token):
        """
        Store token values in keysfile.
        :param access_token:
            Box Access token
        :param refresh_token:
            Box Refresh token
        """
        data = {}
        data['accessToken'] = access_token
        data['refreshToken'] = refresh_token
        REDIS_DB.hmset('box', data)
