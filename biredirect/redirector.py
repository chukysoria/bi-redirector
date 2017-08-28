"""
Redirector
"""
from biredirect.boxstores import BoxKeysStoreRedis
from biredirect.settings import HEROKU_APP_NAME, PORT, REDIS_DB
from boxsdk.exception import BoxOAuthException
from flask import Flask, redirect, request

APP = Flask(__name__)


@APP.route('/redirect', methods=['GET'])
def redirect_to_box():
    """
    Redirect to the Box download address
    """
    doc_id = request.args.get('docID')
    if doc_id is None:
        return 'a'

    new_url = f"https://amadeus.box.com/shared/static/{doc_id}"
    return redirect(new_url)


@APP.route("/authenticate")
def authenticate():
    """
    Launches the authentication process
    """
    oauth = BoxKeysStoreRedis.get_oauth()
    redirect_url = f'https://{HEROKU_APP_NAME}.herokuapp.com/boxauth'
    auth_url, csrf_token = oauth.get_authorization_url(redirect_url)
    REDIS_DB.hset('box', 'csrf_token', csrf_token)
    # Redirect to Box Oauth
    return redirect(auth_url)


@APP.route("/boxauth")
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


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=PORT, debug=True)
