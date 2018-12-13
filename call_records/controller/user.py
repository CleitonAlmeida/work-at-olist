from flask import request
from flask import current_app
from flask_restplus import Resource

from call_records.dto.user import UserDto
from call_records.service.user import get_a_user, get_all_users

api = UserDto.api
userDtoModel = UserDto.user

@api.route('/')
class UserList(Resource):
    @api.doc('list_of_registered_users')
    @api.marshal_list_with(userDtoModel, envelope='data')
    def get(self):
        #current_app.logger.info('Pass in user list get')
        """List all registered users"""
        return get_all_users()

@api.route('/<username>')
@api.param('username', 'The User identifier')
@api.response(404, 'User not found.')
class User(Resource):
    @api.doc('Get a user by username')
    @api.marshal_with(userDtoModel)
    def get(self, username):
        """Get a user given its identifier"""
        user = get_a_user(username)
        if not user:
            api.abort(404, 'User not found.')
        else:
            return user
