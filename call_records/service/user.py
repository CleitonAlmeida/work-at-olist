from call_records.model.user import User
from call_records.service.tokenblacklist import TokenBlackListService
from call_records.service.util import paginated_list
from flask_jwt_extended import get_raw_jwt
from flask import current_app
from flask import request

class UserService(object):

    def save_user(self, data, is_new=True):
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
                new_user.save()
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
                token_service = TokenBlackListService()
                token_service.revoke_user_token(user.username)
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

    def update_user(self, data):
        claims = get_raw_jwt()
        user_claims = claims.get('user_claims')

        # Admin access
        if user_claims.get('is_admin'):
            #Admin user can't revoke your own role
            if data.get('username') == claims.get('identity'):
                data.pop('is_admin', None)
            return self.save_user(data=data, is_new=False)
        # The Own User access
        elif data.get('username') == claims.get('identity'):
            #Normal users cant update your own role
            data.pop('is_admin', None)
            return self.save_user(data=data, is_new=False)
        else:
            response_object = {
                'status': 'fail',
                'message': 'You must be admin'
            }
            return response_object, 403

    def get_a_user(self, username):
        return User.query.filter_by(username=username).first()

    def get_all_users(self, paginated=False, start=None, limit=None):
        if paginated:
            return paginated_list(User, request.base_url, start=start, limit=limit)
        else:
            return User.query.all()
