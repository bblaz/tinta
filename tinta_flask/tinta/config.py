import os


class Config:
    # Default settings
    DEBUG = False
    TESTING = False

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    THREADS_PER_PAGE = 2

    # Settings applicable to all environments
    SECRET_KEY = os.getenv('SECRET_KEY', default="secret")

    CSRF_ENABLED = True
    CSRF_SESSION_KEY = os.getenv('SECRET_KEY', default="secret")
    WTF_CSRF_ENABLED = True

    # Babel defaults
    BABEL_DEFAULT_LOCALE = 'sl'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Ljubljana'

    # Tryton settings
    TRYTON_DATABASE = os.getenv('TRYTON_DATABASE', default="tryton")
    TRYTON_CONFIG = '/etc/trytond.conf'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    RECAPTCHA_ENABLED = False

    TRYTON_DATABASE = 'tinta'
    TRYTON_CONFIG = '/home/blaz/Projects/tinta/.venv/trytond.conf'


class TestingConfig(Config):
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    RECAPTCHA_ENABLED = True

    TRYTON_CONFIG = '/home/blaz/Projects/tinta/.venv/trytond.conf'


class ProductionConfig(Config):
    TRYTON_CONFIG = '/etc/trytond.conf'
