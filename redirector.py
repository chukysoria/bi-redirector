"""
Redirector
"""
from flask import Flask, request, redirect
from settings import PORT

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

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=PORT, debug=True)
