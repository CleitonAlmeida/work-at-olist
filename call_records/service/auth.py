def login_user(data):
    from call_records.model.user import User
    from call_records.service.tokenblacklist import add_token_to_database
    from flask import current_app
    from flask_jwt_extended import (
        JWTManager, jwt_required, create_access_token,
        create_refresh_token, get_jwt_identity
    )

    try:
        user = User.query.filter_by(username=data.get('username')).first()
        if user and user.verify_password(password=data.get('password')):

            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
            add_token_to_database(refresh_token, current_app.config['JWT_IDENTITY_CLAIM'])

            response_object = {
                'status': 'success',
                'message': 'Successfully logged in',
                'access_token': access_token,
                'refresh_token': refresh_token
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
        current_user = current_claims.get('identity')
        user = User.query.filter_by(username=current_user).first()
        if user:
            new_access_token = create_access_token(identity=user)

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
    from call_records.service.tokenblacklist import revoke_user_token
    from flask import current_app
    from flask_jwt_extended import get_raw_jwt
    try:
        #Revoke Current Token
        current_claims = get_raw_jwt()
        revoke_user_token(current_claims.get('identity'))
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
