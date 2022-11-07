# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import os

try:
    from gevent.pywsgi import WSGIServer
except ImportError:
    pass

try:
    from tinta_flask.tinta import create_app
except ImportError:
    from trytond.modules.tinta.tinta_flask.tinta.app import create_app


application = create_app()


if __name__ == "__main__":
    print("Running WSGI server")
    port = int(os.environ.get('PORT', 5000))
    http_server = WSGIServer(('', port), application)
    http_server.serve_forever()
