#!/usr/bin/env python
import os
import sys

from biredirect.redirector import APP
from biredirect.settings import PORT


def main():
    flask_app = APP
    if os.environ.get('DEBUG'):
        flask_app.debug = True

    flask_app.run('0.0.0.0', port=PORT, use_reloader=False, debug=True)


# Only run if script is run directly and not by an import
if __name__ == "__main__":
    sys.exit(main())
