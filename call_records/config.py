import os
# To load .env variables
from dotenv import load_dotenv
load_dotenv()


def env_var(key, default=None, required=False):
    """ Parse environment variable accordingly. """
    if required:
        # Throw KeyError for missing requirements
        val = os.environ[key]
    else:
        # Use default or None
        val = os.environ.get(key, default)

    # Replace booleans
    if val == 'True':
        val = True
    elif val == 'False':
        val = False

    return val


class Config(object):
    """Parent configuration class."""
    # Flask variables
    FLASK_ENV = env_var('FLASK_ENV', default=None)
    FLASK_APP = env_var('FLASK_APP', default='run.py')
    HOST = env_var('HOST', default='0.0.0.0')
    PORT = env_var('PORT', default='5000')
    SERVER_NAME = HOST+':'+PORT

    DEBUG = env_var('DEBUG', default=False)
    CSRF_ENABLED = True
    SECRET_KEY = env_var('SECRET_KEY', required=True)
    # Logging
    LOG_FOLDER = env_var('LOG_FOLDER', default='logs')
    FILE_LOGGING = True

    try:
        if not os.path.exists(LOG_FOLDER) or \
                not os.access(LOG_FOLDER, os.W_OK):
            os.mkdir(LOG_FOLDER)
    except Exception:
        FILE_LOGGING = False

    LOG_NAME = env_var('LOG_NAME', default='info.log')
    LOG_PATH = os.path.join(LOG_FOLDER, LOG_NAME)
    LOG_MAX_BYTES = env_var('LOG_MAX_BYTES', default='100000')
    LOG_BACKUP_COUNT = env_var('LOG_BACKUP_COUNT', default='2')

    ADMIN_USERNAME = env_var('ADMIN_USERNAME', '')
    ADMIN_PASSWORD = env_var('ADMIN_PASSWORD', '')

    PAGINATION_LIMIT = int(env_var('PAGINATION_LIMIT', 20))


class DevelopmentConfig(Config):
    """Configurations for Development."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = env_var('SQLALCHEMY_DATABASE_URI', required=True)


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = env_var('SQLALCHEMY_DATABASE_URI', required=True)
    DEBUG = True


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = env_var('SQLALCHEMY_DATABASE_URI', required=True)


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
