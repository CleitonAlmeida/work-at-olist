from flask import current_app
from flask_restplus import Resource

from call_records.dto.user import UserDto
from call_records.service.user import save_new_user, get_a_user, get_all_users
from flask_restplus import reqparse

ns = UserDto.ns
userDtoModel = UserDto.user

@ns.route('/')
class UserList(Resource):
    @ns.doc('list_of_registered_users')
    @ns.marshal_list_with(userDtoModel, envelope='data')
    def get(self):
        #current_app.logger.info('Pass in user list get')
        """List all registered users"""
        return get_all_users()

    @ns.param('username', 'The User identifier')
    @ns.param('password', 'The password')
    def post(self):
        """Create a new user"""
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        data = parser.parse_args()

        return save_new_user(data=data)


@ns.route('/<username>')
@ns.param('username', 'The User identifier')
@ns.response(404, 'User not found.')
class User(Resource):
    @ns.doc('Get a user by username')
    @ns.marshal_with(userDtoModel)
    def get(self, username):
        """Get a user given its identifier"""
        user = get_a_user(username)
        if not user:
            ns.abort(404, 'User not found.')
        else:
            return user
