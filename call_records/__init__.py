# app/__init__.property

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
import logging
from . import home
from .config import app_config
from flask.logging import default_handler

db = SQLAlchemy()

def configure_db(app):
    db.init_app(app)

def configure_logging(app, config_name):
    """ Configure logging. """
    # Skip logging configuration for debug mode.
    if app.debug or not app.config['FILE_LOGGING']:
        return

    # http://flask.pocoo.org/docs/errorhandling/
    app.logger.setLevel(logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_file_handler = RotatingFileHandler(app_config[config_name].LOG_PATH, int(app_config[config_name].LOG_MAX_BYTES), int(app_config[config_name].LOG_BACKUP_COUNT))
    log_file_handler.setLevel(logging.INFO)
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

    app.logger.addHandler(log_file_handler)
    logger.addHandler(log_file_handler)

def configure_blueprint(app):
    app.register_blueprint(home.bp)

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    configure_logging(app, config_name)
    configure_blueprint(app)
    configure_db(app)

    return app
