"""
Redirector
"""
from functools import wraps
import json
from os import environ as env
from urllib.parse import urlparse

from auth0.v3.authentication import GetToken, Users
from boxsdk.exception import BoxOAuthException
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, session)

from biredirect.boxstores import BoxKeysStoreRedis
from biredirect.settings import (AUTH0_CALLBACK_URL, AUTH0_CLIENT_ID,
                                 AUTH0_CLIENT_SECRET, AUTH0_DOMAIN,
                                 HEROKU_APP_NAME, REDIS_DB)

APP = Flask(__name__)
APP.secret_key = 'secret'  # TODO: Replace by real secret

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

# Static files routes
@APP.route('/')
def home():
    return render_template('home.html', env=env)

@APP.route('/public/<path:filename>')
def static_files(filename):
    return send_from_directory('./public', filename)


@APP.route('/dashboard')
@requires_auth
def dashboard():
    return 'Future dashboard'

@APP.route('/logout')
def logout():
    session.clear()
    base_url = f'https://{HEROKU_APP_NAME}.herokuapp.com/'
    return redirect(f'https://{AUTH0_DOMAIN}/v2/logout?returnTo={base_url}&client_id={AUTH0_CLIENT_ID}')


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

@APP.route('/api/redirect/onedrive', methods=['GET'])
def redirect_to_onedrive():
    """
    Redirect to the OneDrive download address
    """
    filename = request.args.get('filename')
    if filename is None:
        new_url = "https://myoffice.accenture.com/personal/c_sanchez_mateo_accenture_com/Documents/IFTTT/Gmail/BaseExport.csv"
    else:
        new_url = f"https://myoffice.accenture.com/personal/c_sanchez_mateo_accenture_com/Documents/IFTTT/Gmail/{filename}"

    return redirect(new_url)

# Here we're using the /callback route.
@APP.route('/api/authcallback')
def callback_handling():
    code = request.args.get('code')
    redirectUrl = request.args.get('redirectto')
    get_token = GetToken(AUTH0_DOMAIN)
    auth0_users = Users(AUTH0_DOMAIN)
    token = get_token.authorization_code(AUTH0_CLIENT_ID,
                                         AUTH0_CLIENT_SECRET, code, AUTH0_CALLBACK_URL)
    user_info = auth0_users.userinfo(token['access_token'])
    session['profile'] = json.loads(user_info)
    return redirect(redirectUrl)


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
