# app/__init__.property

from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
import logging
from . import home
from .config import app_config
from flask.logging import default_handler
from flask_jwt_extended import JWTManager

from call_records.controller.user import User as UserController
from call_records.dto.user import UserDto

db = SQLAlchemy()

def configure_db(app):
    db.init_app(app)

def configure_logging(app, config_name):
    """ Configure logging. """

    # http://flask.pocoo.org/docs/errorhandling/
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_file_handler = RotatingFileHandler(app_config[config_name].LOG_PATH, int(app_config[config_name].LOG_MAX_BYTES), int(app_config[config_name].LOG_BACKUP_COUNT))
    log_file_handler.setLevel(logging.INFO)
    log_file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

    logger.addHandler(log_file_handler)
    app.logger.removeHandler(default_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(log_file_handler)

def configure_blueprint(app):
    app.register_blueprint(home.bp)

def configure_namespace(app):
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }
    api = Api(app,
              title='FLASK API CALL RECORDS',
              version='1.0',
              description='An api for receives call detail records and calculates monthly bills',
              doc='/api',
              authorizations=authorizations,
              security='Bearer Auth')
    api.add_namespace(UserDto.ns, path='/user')

def configure_jwt(app):
    app.config['JWT_SECRET_KEY'] = 'AUIRgoasdgfuyAUYFaisuebf'  # Change this!
    jwt = JWTManager(app)

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    configure_logging(app, config_name)
    configure_db(app)
    configure_jwt(app)
    configure_blueprint(app)
    configure_namespace(app)


    return app
