from flask import current_app
from flask_restplus import Resource

from call_records.dto.user import UserDto
from call_records.service.user import (save_user, get_a_user, get_all_users,
    update_user)
from call_records.controller import user_required, admin_required
from flask_restplus import reqparse, inputs

ns = UserDto.ns
userDtoModel = UserDto.user
userListDtoModel = UserDto.userList
userResponseDtoModel = UserDto.userResponses

def get_parser_user():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    return parser

def get_parser_update_user():
    parser = reqparse.RequestParser()
    parser.add_argument('is_admin', type=inputs.boolean, required=False, help='The role of user (if admin or not admin)')
    parser.add_argument('password', type=str, required=True)
    return parser

def get_parser_pagination():
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=int, required=False, default=1)
    parser.add_argument('limit', type=int, required=False)
    return parser

@ns.route('/')
class User(Resource):
    @admin_required
    @ns.expect(get_parser_pagination(), validate=True)
    @ns.marshal_list_with(userListDtoModel, envelope='data', skip_none=True)
    def get(self, page=None):
        """List all registered users"""
        parser = get_parser_pagination()
        data = parser.parse_args()
        return get_all_users(paginated=True, start=data.get('start'), limit=data.get('limit'))

    @admin_required
    @ns.expect(get_parser_user(), validate=True)
    @ns.doc(responses={
        201: 'Successfully registered',
        409: 'User already exists. Please Log in'
    })
    def post(self):
        """Create a new user"""
        parser = get_parser_user()
        data = parser.parse_args()
        return save_user(data=data)


@ns.route('/<username>')
@ns.param('username', 'The User identifier')
@ns.response(404, 'User not found.')
class UserSpecific(Resource):
    @admin_required
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

    @user_required
    @ns.expect(get_parser_update_user(), validate=True)
    @ns.marshal_with(userResponseDtoModel, skip_none=True)
    @ns.doc(responses={
        200: 'Successfully updated',
        404: 'User not found'
    })
    def put(self, username):
        """To update an user"""
        try:
            parser = get_parser_update_user()
            data = parser.parse_args()
            data['username'] = username
            return update_user(data=data)
        except Exception as e:
            current_app.logger.error('user/<username> %s', e)
            response_object = {
                'status': 'fail',
                'message': 'Try again'
            }
            return response_object, 500
