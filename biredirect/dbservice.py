import os
from urllib.parse import urlparse

from redis import StrictRedis

from biredirect.settings import REDIS_SECURE, REDIS_URL


class DBService(object):

    LUA_NEW_ITEM = """
local r1 = redis.call("HMSET",  KEYS[1] .. ":" .. KEYS[2], unpack(ARGV))
local r2 = redis.call("SADD", KEYS[1], KEYS[2])
return r1, r2
"""
    CONFIG_KEY = "config"
    BOX_KEY = "box"

    def __init__(self, database_url=REDIS_URL):
        url_parts = urlparse(database_url)
        # Secure port in next port given in production
        port = url_parts.port + REDIS_SECURE
        self._redis = StrictRedis(host=url_parts.hostname, port=port, password=url_parts.password, decode_responses=True)
        # Register scripts
        self._new_config = self._redis.register_script(self.LUA_NEW_ITEM)

    # Config
    def insert_config(self, data):
        args = []
        for key, value in data.items():
            args.append(key)
            args.append(value)
        result = self._new_config(
            keys=[self.CONFIG_KEY, data['name']],
            args=args)
        if result == 'OK':
            return self.get_config(data['name'])
        self.delete_config(data['name'])
        return None

    def get_configs(self):
        config_names = self._redis.smembers(self.CONFIG_KEY)
        pipe = self._redis.pipeline()
        for config_name in config_names:
            pipe.hgetall(f'{self.CONFIG_KEY}:{config_name}')

        configs = pipe.execute()
        for config in configs:
            if 'secure' in config:
                config['secure'] = config['secure'] == 'True'
        return configs

    def get_config(self, config_name):
        config = self.get_hash_keys(f'{self.CONFIG_KEY}:{config_name}')
        if 'secure' in config:
            config['secure'] = config['secure'] == 'True'
        return config

    def get_config_value(self, config_name):
        return self.get_hash_key(f'{self.CONFIG_KEY}:{config_name}', 'value')

    def update_config(self, config_name, data):
        args = []
        for key, value in data.items():
            args.append(key)
            args.append(value)
        if self.set_hash_keys(f'{self.CONFIG_KEY}:{config_name}', data):
            config = self.get_config(config_name)
            return config
        return None

    def delete_config(self, config_name):
        pipe = self._redis.pipeline()
        pipe.delete(f'{self.CONFIG_KEY}:{config_name}')
        pipe.srem(self.CONFIG_KEY, config_name)
        result = pipe.execute()
        if result == [1, 1]:
            return 'Ok'
        return None

    def config_exists(self, config_name):
        return self._redis.sismember(self.CONFIG_KEY, config_name) == 1

    # Box
    def set_crsf_token(self, csrf_token):
        self._redis.hset(self.BOX_KEY, 'csrf_token', csrf_token)

    def get_crsf_token(self):
        return self.get_hash_key(self.BOX_KEY, 'csrf_token')

    # Common
    def get_hash_keys(self, name):
        return self._redis.hgetall(name)

    def get_hash_key(self, name, key):
        return self._redis.hget(name, key)

    def set_hash_keys(self, name, mapping):
        return self._redis.hmset(name, mapping)
