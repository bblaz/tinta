# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import logging
import os

from flask import Flask, url_for
from flask.logging import default_handler

from flask_babel import Babel
from flask_tryton import Tryton

from psycopg2.errors import UndefinedTable


babel = Babel()
tryton = Tryton(None, configure_jinja=True)

try:
    import tinta.config as _cfg
    config = 'tinta_flask.tinta.config.'
except ImportError:
    import trytond.modules.tinta.flask_tinta.config as _cfg     # noqa
    config = 'trytond.modules.tinta.flask_tinta.config.'


config = config + os.getenv('TINTA_CONFIG', default='ProductionConfig')

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(
        dsn=os.getenv("LOG_SENTRY_URL", None),
        integrations=[FlaskIntegration()],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
        )


except ImportError:
    pass


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # for key, value in app.config.items():
    #     print("%s : %s" % (key, value))

    ok = initialize_extensions(app)

    register_blueprints(app, ok)

    configure_logging(app)

    if ok:
        register_error_handlers(app)

        register_custom_filters(app)

        register_custom_context(app)

    return app


def register_blueprints(app, ok=True):
    from . import main
    app.register_blueprint(main.main)


def initialize_extensions(app):
    babel.init_app(app)
    try:
        tryton.init_app(app)
    except UndefinedTable:
        print("Database not initialized.")
        return False
    return True


def configure_logging(app):
    for logger in (app.logger, logging.getLogger('trytond')):
        logger.addHandler(default_handler)
        logger.setLevel(logging.INFO)


def register_error_handlers(app):
    pass


def register_custom_filters(app):
    with app.app_context():
        from . import filters       # noqa


def register_custom_context(app):
    with app.app_context():
        from . import context       # noqa
