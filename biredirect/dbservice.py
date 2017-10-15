from redis import StrictRedis

from biredirect.settings import REDIS_URL


class DBService(object):

    LUA_NEW_ITEM = """
local r1 = redis.call("HMSET",  KEYS[1] .. ":" .. KEYS[2], unpack(ARGV))
local r2 = redis.call("SADD", KEYS[1], KEYS[2])
return r1, r2
"""
    CONFIG_KEY = "config"
    BOX_KEY = "box"

    def __init__(self, database_url=REDIS_URL):
        self._redis = StrictRedis.from_url(database_url, decode_responses=True)
        # Register scripts
        self._new_config = self._redis.register_script(self.LUA_NEW_ITEM)

    # Config
    def insert_config(self, data):
        result = self._new_config(
            keys=[self.CONFIG_KEY, data['name']],
            args=['name', data['name'],
                  'value', data['value']])
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
        return configs

    def get_config(self, config_name):
        return self.get_hash_keys(f'{self.CONFIG_KEY}:{config_name}')

    def get_config_value(self, config_name):
        return self.get_hash_key(f'{self.CONFIG_KEY}:{config_name}', 'value')

    def update_config(self, config_name, data):
        if self.set_hash_keys(f'{self.CONFIG_KEY}:{config_name}',
                              {'name': data['name'], 'value': data['value']}):
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
