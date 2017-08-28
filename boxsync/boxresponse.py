"""
Simple webserver to retrieve a Box auth response.
"""
from boxsdk.exception import BoxOAuthException
from flask import Flask, request

FLASK_APP = Flask(__name__)


def shutdown_server():
    """
    Shutdowns webserver.

    :raise:
        :class:`RuntimeError`
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@FLASK_APP.route("/boxauth")
def boxauth():
    """
    Stores the received tokens in oauth.
    """
    csrf_token = request.args.get('state')
    auth_token = request.args.get('code')
    assert FLASK_APP.config['csrf_token'] == csrf_token
    try:
        FLASK_APP.config['oauth'].authenticate(auth_token)
        response = "Authenticated. You can close this window."
    except BoxOAuthException as ex:
        response = ex._message["error_description"]
    shutdown_server()
    return response
