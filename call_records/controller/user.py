from flask import current_app
from call_records import fixed
from call_records.dto.user import UserDto
from call_records.service.user import UserService
from call_records.controller import user_required, admin_required
from flask_restplus import Resource, Namespace
from flask_restplus import reqparse, inputs

service = UserService()
ns = Namespace('user', description='User')
dto = UserDto(ns)


def get_parser_user():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username')
    parser.add_argument('password', type=str, required=True, help='Password')
    return parser


def get_parser_update_user():
    parser = reqparse.RequestParser()
    parser.add_argument('is_admin', type=inputs.boolean, required=False,
                        help='The role of user (if admin or not admin)')
    parser.add_argument('password', type=str,
                        required=True, help='User password')
    return parser


def get_parser_pagination():
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=int, required=False, default=1,
                        help='The position from which the data will'+
                            ' be returned')
    parser.add_argument('limit', type=int, required=False,
                        help='The max number of items to return'+
                            ' from the current position')
    return parser


@ns.route('/')
class User(Resource):
    @admin_required
    @ns.expect(get_parser_pagination(), validate=True)
    @ns.marshal_list_with(dto.userList, envelope='data', skip_none=True)
    def get(self, page=None):
        """List all registered users"""
        parser = get_parser_pagination()
        data = parser.parse_args()
        return service.get_all_users(paginated=True,
                                     start=data.get('start'),
                                     limit=data.get('limit'))

    @admin_required
    @ns.expect(get_parser_user(), validate=True)
    @ns.doc(responses={
        201: fixed.MSG_SUCCESSFULLY_REGISTRED,
        409: fixed.MSG_USER_EXISTING
    })
    def post(self):
        """To create a new user"""
        parser = get_parser_user()
        data = parser.parse_args()
        return service.save_user(data=data)


@ns.route('/<username>')
@ns.param('username', 'The User identifier')
@ns.response(404, fixed.MSG_USER_NOT_FOUND)
class UserSpecific(Resource):
    @admin_required
    @ns.marshal_with(dto.user)
    @ns.doc(responses={
        200: 'Success',
        404: fixed.MSG_USER_NOT_FOUND
    })
    def get(self, username):
        """Get an user given its identifier"""
        user = service.get_a_user(username)
        if not user:
            ns.abort(404, fixed.MSG_USER_NOT_FOUND)
        else:
            return user

    @user_required
    @ns.expect(get_parser_update_user(), validate=True)
    @ns.marshal_with(dto.userResponses, skip_none=True)
    @ns.doc(responses={
        200: fixed.MSG_SUCCESSFULLY_UPDATED,
        404: fixed.MSG_USER_NOT_FOUND
    })
    def put(self, username):
        """To update an user"""
        try:
            parser = get_parser_update_user()
            data = parser.parse_args()
            data['username'] = username
            return service.update_user(data=data)
        except Exception as e:
            current_app.logger.error('user/<username> %s', e)
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_TRY_AGAIN
            }
            return response_object, 500
