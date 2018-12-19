def save_changes(data):
    from call_records import db
    db.session.add(data)
    db.session.commit()

def save_user(data, is_new=True):
    from call_records.model.user import User
    from call_records.service.tokenblacklist import revoke_token_user
    from flask import current_app

    try:
        user = User.query.filter_by(username=data['username']).first()
        #New user
        if not user and is_new:
            new_user = User(
                username = data['username'],
                password_hash = data['password'],
                is_admin = data.get('is_admin', False)
            )
            new_user.gen_hash(data['password'])
            save_changes(new_user)
            response_object = {
                'status': 'success',
                'message': 'Successfully registered'
            }
            return response_object, 201
        #Existing User
        elif user and not is_new:
            user.gen_hash(data['password'])
            user.is_admin = data.get('is_admin')
            user.save()
            """
            When a password update occurs, we need to revoke the tokens
            to force a new login
            """
            revoke_token_user(user.username)
            response_object = {
                'status': 'success',
                'message': 'Successfully updated'
            }
            return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'User already exists. Please Log in',
            }
            return response_object, 409
    except Exception as e:
        current_app.logger.error('save_user %s', e)
        response_object = {
            'status': 'fail',
            'message': e
        }
        return response_object, 500

def update_user(data):
    from flask_jwt_extended import get_raw_jwt
    from flask import current_app

    claims = get_raw_jwt()
    user_claims = claims.get('user_claims')

    # Admin access
    if user_claims.get('is_admin'):
        #Admin user can't revoke your own role
        if data.get('username') == claims.get('identity'):
            data.pop('is_admin', None)
        return save_user(data=data, is_new=False)
    # The Own User access
    elif data.get('username') == claims.get('identity'):
        #Normal users cant update your own role
        data.pop('is_admin', None)
        return save_user(data=data, is_new=False)
    else:
        response_object = {
            'status': 'fail',
            'message': 'You must be admin'
        }
        return response_object, 401

def check_first_admin_user():
    """
    Verify if exists an user admin, and if not, create
    The system can not be run securely containing the admin password in the var ADMIN_PASSWORD
    then, for safety, this function check this and log this event as a warning.(if necessary)
    """
    from flask import current_app
    from call_records.model.user import User
    username = current_app.config.get('ADMIN_USERNAME')
    password = current_app.config.get('ADMIN_PASSWORD')
    if username and password:
        #current_app.app_context().push()
        user_admin = User.query.filter((User.username==username) | (User.is_admin==True)).first()
        if not user_admin:
            data = {'username': username, 'password': password, 'is_admin': True}
            save_user(data)
        if user_admin.verify_password(password=password):
            current_app.logger.warning('The user\'s password remains the same as the one defined in the .env file. For security it is necessary to change it')

def get_a_user(username):
    from call_records.model.user import User
    return User.query.filter_by(username=username).first()

def get_a_user_or_admin(username):
    from call_records.model.user import User
    return User.query.filter((User.username==username) | (User.is_admin==True)).first()

def get_all_users():
    from call_records.model.user import User
    return User.query.all()

def login_user(data):
    from call_records.model.user import User
    from call_records.service.tokenblacklist import add_token_to_database
    from flask import current_app
    from flask_jwt_extended import (
        JWTManager, jwt_required, create_access_token,
        get_jwt_identity
    )

    try:
        user = User.query.filter_by(username=data.get('username')).first()
        if user and user.verify_password(password=data.get('password')):
            access_token = create_access_token(identity=user)
            add_token_to_database(access_token, current_app.config['JWT_IDENTITY_CLAIM'])
            response_object = {
                'status': 'success',
                'message': 'Successfully logged in',
                'access_token': access_token
            }
            return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'Username or password does not match.'
            }
            return response_object, 401
    except Exception as e:
        current_app.logger.error('login_user %s', e)
        response_object = {
            'status': 'fail',
            'message': 'Try again'
        }
        return response_object, 500

def get_refresh_token():
    from flask_jwt_extended import create_access_token, get_raw_jwt
    from flask import current_app
    from call_records.model.user import User
    from call_records.service.tokenblacklist import add_token_to_database, revoke_token

    try:
        #Revoke Current Token
        current_claims = get_raw_jwt()
        revoke_token(current_claims.get('jti'), current_claims.get('identity'))
        current_user = current_claims.get('identity')
        user = User.query.filter_by(username=current_user).first()
        if user:
            new_access_token = create_access_token(identity=user)
            add_token_to_database(new_access_token, current_app.config['JWT_IDENTITY_CLAIM'])
            response_object = {
                'status': 'success',
                'access_token': new_access_token
            }
            return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'User does not match.'
            }
            return response_object, 401
    except Exception as e:
        current_app.logger.error('get_refresh_token %s', e)
        response_object = {
            'status': 'fail',
            'message': 'Try again'
        }
        return response_object, 500

def logout_user():
    from call_records.service.tokenblacklist import revoke_token_user
    from flask import current_app
    from flask_jwt_extended import get_raw_jwt
    try:
        #Revoke Current Token
        current_claims = get_raw_jwt()
        revoke_token_user(current_claims.get('identity'))
        response_object = {
            'status': 'success',
            'message': 'Logout Successfully'
        }
        return response_object, 200
    except Exception as e:
        current_app.logger.error('logout_user %s', e)
        response_object = {
            'status': 'fail',
            'message': 'Try again'
        }
        return response_object, 500
