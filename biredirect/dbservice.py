from redis import StrictRedis

from biredirect.settings import REDIS_URL


class DBService(object):

    LUA_NEW_ITEM = """
local id = redis.call("INCR", KEYS[1] .. ":id")
redis.call("HMSET",  KEYS[1] .. ":" .. id, unpack(ARGV))
redis.call("SADD", KEYS[1], id)
return id
"""
    CONFIG_KEY = "config"
    BOX_KEY = "box"

    def __init__(self, database_url=REDIS_URL):
        self._redis = StrictRedis.from_url(database_url, decode_responses=True)
        # Register scripts
        self._new_config = self._redis.register_script(self.LUA_NEW_ITEM)

    # Config

    def insert_config(self, data):
        config_id = self._new_config(keys=[self.CONFIG_KEY],
                                     args=['name', data['name'],
                                           'value', data['value']])
        config = self._redis.hgetall(f'{self.CONFIG_KEY}:{config_id}')
        config['id'] = config_id
        return config

    def retrieve_configs(self):
        config_ids = self._redis.smembers(self.CONFIG_KEY)
        pipe = self._redis.pipeline()
        for config_id in config_ids:
            pipe.hgetall(f'{self.CONFIG_KEY}:{config_id}')

        configs = pipe.execute()
        i = 0
        for config_id in config_ids:
            configs[i]['id'] = config_id
            i += 1
        return configs

    def get_config(self, config_id):
        config = self._redis.hgetall(f'{self.CONFIG_KEY}:{config_id}')
        if config:
            config['id'] = config_id
            return config
        return None

    def update_config(self, config_id, data):
        if self._redis.hmset(f'{self.CONFIG_KEY}:{config_id}',
                             {'name': data['name'], 'value': data['value']}):
            config = self.get_config(config_id)
            return config
        return None

    def delete_config(self, config_id):
        pipe = self._redis.pipeline()
        pipe.delete(f'{self.CONFIG_KEY}:{config_id}')
        pipe.srem('config', config_id)
        result = pipe.execute()
        if result == [1, 1]:
            return 'Ok'
        return None

    # Box

    def set_crsf_token(self, csrf_token):
        self._redis.hset(self.BOX_KEY, 'csrf_token', csrf_token)

    def get_crsf_token(self):
        return self._redis.hget(self.BOX_KEY, 'csrf_token')
