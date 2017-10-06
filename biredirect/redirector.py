"""
Redirector
"""
import json
from functools import wraps

from auth0.v3.authentication import GetToken, Users
from boxsdk.exception import BoxOAuthException
from flask import (Flask, jsonify, redirect, request,
                   send_from_directory, session)

from biredirect.boxstores import BoxKeysStoreRedis
from biredirect.settings import (AUTH0_CALLBACK_URL, AUTH0_CLIENT_ID,
                                 AUTH0_CLIENT_SECRET, AUTH0_DOMAIN,
                                 HEROKU_APP_NAME, REDIS_DB)

APP = Flask(__name__)
APP.secret_key = 'secret'  # TODO: Replace by real secret


# Login decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            # Redirect to Login page here
            return redirect('/')
        return f(*args, **kwargs)

    return decorated


# API Routes
@APP.route('/api/redirect', methods=['GET'])
def redirect_to_box():
    """
    Redirect to the Box download address
    """
    doc_id = request.args.get('docID')
    if doc_id is None:
        return 'a'

    new_url = f"https://amadeus.box.com/shared/static/{doc_id}"
    return redirect(new_url)

LUA_NEW_ITEM = """
local id = redis.call("INCR", KEYS[1] .. ":id")
redis.call("HMSET",  KEYS[1] .. ":" .. id, unpack(ARGV))
redis.call("SADD", KEYS[1], id)
return id
"""

@APP.route('/api/configs', methods=['POST'])
def create_config():
    data = request.json
    new_config = REDIS_DB.register_script(LUA_NEW_ITEM)
    config_id = new_config(keys=['config'], args=['name', data['name'], 'value', data['value']])
    config = REDIS_DB.hgetall(f'config:{config_id}')
    config['id'] = config_id
    return jsonify({'data': config}), 201


@APP.route('/api/configs', methods=['GET'])
def retrieve_configs():
    """
    Return all configs
    """
    config_ids = REDIS_DB.smembers('config')
    pipe = REDIS_DB.pipeline()
    for config_id in config_ids:
        pipe.hgetall(f'config:{config_id}')

    configs = pipe.execute()
    i = 0
    for config_id in config_ids:
        configs[i]['id'] = config_id
        i += 1
    return jsonify({'data': configs})

def get_config(config_id):
    config = REDIS_DB.hgetall(f'config:{config_id}')
    if config:
        config['id'] = config_id
        return config
    return None

@APP.route('/api/configs/<int:config_id>', methods=['GET'])
def retrieve_config(config_id):
    config = get_config(config_id)
    if config:
        return jsonify({'data': config})
    return jsonify({"error": "id doesn't exist"}), 404


@APP.route('/api/configs/<int:config_id>', methods=['PUT'])
def update_config(config_id):
    data = request.json
    if REDIS_DB.hmset(f'config:{config_id}', {'name': data['name'], 'value': data['value']}):
        config = get_config(config_id)
        if config:
            return jsonify({'data': config})
    return jsonify({'error': 'Not updated'})


@APP.route('/api/configs/<int:config_id>', methods=['DELETE'])
def delete_config(config_id):
    pipe = REDIS_DB.pipeline()
    pipe.delete(f'config:{config_id}')
    pipe.srem('config', config_id)
    result = pipe.execute()
    if result == [1, 1]:
        return jsonify({'result': 'success'})
    return jsonify({'error': 'Not deleted'}), 404


# Internal Logins
@APP.route('/api/authcallback')
def callback_handling():
    error = request.args.get('error')
    if error is None:
        code = request.args.get('code')
        redirect_url = request.args.get('redirectto')
        if redirect_url is None:
            redirect_url = '/'
        get_token = GetToken(AUTH0_DOMAIN)
        auth0_users = Users(AUTH0_DOMAIN)
        token = get_token.authorization_code(AUTH0_CLIENT_ID,
                                             AUTH0_CLIENT_SECRET,
                                             code, AUTH0_CALLBACK_URL)
        user_info = auth0_users.userinfo(token['access_token'])
        session['profile'] = json.loads(user_info)
        return redirect(redirect_url)
    else:
        error_msg = request.args.get('error_description')
        return f'<h1>{error}</h1><p>{error_msg}<p>', 401


@APP.route('/logout')
def logout():
    session.clear()
    base_url = f'https://{HEROKU_APP_NAME}.herokuapp.com/'
    return redirect(
        f'https://{AUTH0_DOMAIN}/v2/logout?'
        f'returnTo={base_url}&client_id={AUTH0_CLIENT_ID}')


# Box logins
@APP.route("/api/authenticate")
def authenticate():
    """
    Launches the authentication process
    """
    oauth = BoxKeysStoreRedis.get_oauth()
    redirect_url = f'https://{HEROKU_APP_NAME}.herokuapp.com/api/boxauth'
    auth_url, csrf_token = oauth.get_authorization_url(redirect_url)
    REDIS_DB.hset('box', 'csrf_token', csrf_token)
    # Redirect to Box Oauth
    return redirect(auth_url)


@APP.route("/api/boxauth")
def boxauth():
    """
    Stores the received tokens in oauth.
    """
    csrf_token = request.args.get('state')
    auth_token = request.args.get('code')
    try:
        assert REDIS_DB.hget('box', 'csrf_token') == csrf_token
        BoxKeysStoreRedis.get_oauth().authenticate(auth_token)
        response = "Authenticated. You can close this window."
    except BoxOAuthException as ex:  # pragma: no cover
        response = ex
    except AssertionError:
        response = "Tokens don't match"
    return response

# Fileserver


# Catch All urls, enabling copy-paste url
@APP.route('/', defaults={'path': ''})
@APP.route('/<path:path>')  # Catch All urls, enabling copy-paste url
def home(path):
    print('here: %s' % path)
    if path == '':
        path = 'index.html'
    return send_from_directory('./dist', path)


@APP.route('/dashboard')
@requires_auth
def dashboard():
    return 'Future dashboard'
