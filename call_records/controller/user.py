from flask import current_app
from flask_restplus import Resource

from call_records.dto.user import UserDto
from call_records.service.user import save_new_user, get_a_user, get_all_users, login_user
from call_records.controller import user_required
from flask_restplus import reqparse

ns = UserDto.ns
userDtoModel = UserDto.user
userLogInDtoModel = UserDto.userLogIn

def get_parser_user():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    return parser

@ns.route('/')
class User(Resource):
    @user_required
    @ns.marshal_list_with(userDtoModel, envelope='data', skip_none=True)
    def get(self):
        #current_app.logger.info('Pass in user list get')
        """List all registered users"""
        return get_all_users()

    @user_required
    @ns.expect(get_parser_user(), validate=True)
    @ns.doc(responses={
        201: 'Successfully registered',
        409: 'User already exists. Please Log in'
    })
    def post(self):
        """Create a new user"""
        parser = get_parser_user()
        data = parser.parse_args()

        return save_new_user(data=data)


@ns.route('/<username>')
@ns.param('username', 'The User identifier')
@ns.response(404, 'User not found.')
class UserSpecific(Resource):
    @user_required
    @ns.marshal_with(userDtoModel)
    @ns.doc(responses={
        200: 'Success',
        404: 'User not found'
    })
    def get(self, username):
        """Get an user given its identifier"""
        user = get_a_user(username)
        if not user:
            ns.abort(404, 'User not found.')
        else:
            return user

@ns.route('/login')
class UserLogin(Resource):
    @ns.expect(get_parser_user(), validate=True)
    @ns.marshal_with(userLogInDtoModel, skip_none=True)
    @ns.doc(responses={
        200: 'Success',
        401: 'Username or password does not match'
    })
    @ns.doc(security=[])
    def post(self):
        """To Login in"""
        parser = get_parser_user()
        data = parser.parse_args()

        return login_user(data=data)
