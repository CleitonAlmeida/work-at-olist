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

from call_records.controller import page_not_found
from call_records.dto.auth import AuthDto

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

def configure_restplus(app, jwt):
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

    from call_records.controller import call, user, auth

    api.add_namespace(auth.ns, path='/api')
    api.add_namespace(user.ns, path='/api/user')
    api.add_namespace(call.ns, path='/api/call')

    #https://github.com/vimalloc/flask-jwt-extended/issues/86
    jwt._set_error_handler_callbacks(api)

def configure_jwt(app):
    app.config['JWT_SECRET_KEY'] = 'AUIRgoasdgfuyAUYFaisuebf'  # Change this!
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    jwt = JWTManager(app)

    # Create a function that will be called whenever create_access_token
    # is used. It will take whatever object is passed into the
    # create_access_token method, and lets us define what custom claims
    # should be added to the access token.
    @jwt.user_claims_loader
    def add_claims_to_access_token(user):
        return {'is_admin': user.is_admin}

    # Create a function that will be called whenever create_access_token
    # is used. It will take whatever object is passed into the
    # create_access_token method, and lets us define what the identity
    # of the access token should be.
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.username

    # Define our callback function to check if a token has been revoked or not
    @jwt.token_in_blacklist_loader
    def check_if_token_revoked(decoded_token):
        from call_records.service.tokenblacklist import is_token_revoked
        return is_token_revoked(decoded_token)

    return jwt

def configure_user_admin(app):
    username = app.config.get('ADMIN_USERNAME')
    password = app.config.get('ADMIN_PASSWORD')

    if username and password:
        app.app_context().push()
        from call_records.service.user_check import check_first_admin_user
        check_first_admin_user()

def configure_error_handler(app):
    app.register_error_handler(404, page_not_found)

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    configure_error_handler(app)
    configure_logging(app, config_name)
    configure_db(app)
    configure_blueprint(app)
    jwt = configure_jwt(app)
    configure_restplus(app, jwt)
    configure_user_admin(app)

    return app
