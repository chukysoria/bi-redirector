"""
Redirector
"""
import json
from functools import wraps
from os import environ as env

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


configs = [
    {'id': 0, 'name': 'Public Key', 'value': 'a12'},
    {'id': 1, 'name': 'Secret Key', 'value': '0asf'}
]


@APP.route('/api/configs', methods=['POST'])
def create_config():
    data = request.json
    last_id = configs[-1]['id']
    new_config = {'id': last_id + 1,
                  'name': data['name'], 'value': data['value']}
    configs.append(new_config)
    config = configs[-1]
    return jsonify({'data': config}), 201


@APP.route('/api/configs', methods=['GET'])
def retrieve_configs():
    """
    Return all configs
    """
    return jsonify({'data': configs})


@APP.route('/api/configs/<int:config_id>', methods=['GET'])
def retrieve_config(config_id):
    config = [config for config in configs if config['id'] == config_id][0]
    if config:
        return jsonify({'data': config})
    return jsonify({"error": "id doesn't exist"}), 404


@APP.route('/api/configs/<int:config_id>', methods=['PUT'])
def update_config(config_id):
    config = [config for config in configs if config['id'] == config_id][0]
    data = request.json
    config['name'] = data['name']
    config['value'] = data['value']
    return jsonify({'data': config})


@APP.route('/api/configs/<int:config_id>', methods=['DELETE'])
def delete_config(config_id):
    config = [config for config in configs if config['id'] == config_id][0]
    configs.remove(config)
    return jsonify({'result': 'success'})


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
