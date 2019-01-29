from call_records.service.tokenblacklist import TokenBlackListService
from call_records.model.user import User
from call_records import fixed
from flask import current_app
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token, get_jwt_identity, get_raw_jwt
)


class AuthService(object):

    def login_user(self, data):
        try:
            user = User.query.filter_by(username=data.get('username')).first()
            if user and user.verify_password(password=data.get('password')):

                access_token = create_access_token(identity=user)
                refresh_token = create_refresh_token(identity=user)
                token_service = TokenBlackListService()
                token_service.add_token_to_database(
                    refresh_token, current_app.config['JWT_IDENTITY_CLAIM'])

                response_object = {
                    'status': 'success',
                    'message': fixed.MSG_SUCCESS_LOGIN,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
                return response_object, 200
            else:
                response_object = {
                    'status': 'fail',
                    'message': fixed.MSG_FAILED_LOGIN
                }
                return response_object, 401
        except Exception as e:
            current_app.logger.error('login_user %s', e)
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_TRY_AGAIN
            }
            return response_object, 500

    def get_refresh_token(self):
        try:
            # Revoke Current Token
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
                    'message': fixed.MSG_FAILED_LOGIN
                }
                return response_object, 401
        except Exception as e:
            current_app.logger.error('get_refresh_token %s', e)
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_TRY_AGAIN
            }
            return response_object, 500

    def logout_user(self):
        try:
            # Revoke Current Token
            current_claims = get_raw_jwt()
            token_service = TokenBlackListService()
            token_service.revoke_user_token(current_claims.get('identity'))
            response_object = {
                'status': 'success',
                'message': fixed.MSG_SUCCESS_LOGOUT
            }
            return response_object, 200
        except Exception as e:
            current_app.logger.error('logout_user %s', e)
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_TRY_AGAIN
            }
            return response_object, 500
