from flask import current_app
from flask_restplus import Resource, Namespace
from flask_restplus import reqparse
from flask_jwt_extended import jwt_refresh_token_required, get_raw_jwt

from call_records.controller import user_required
from call_records.dto.auth import AuthDto
from call_records.service.auth import AuthService

service = AuthService()
ns = Namespace('auth', description='Auth')
dto = AuthDto(ns)


def get_login_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    return parser

@ns.route('/login')
class UserLogin(Resource):
    @ns.expect(get_login_parser(), validate=True)
    @ns.marshal_with(dto.authLogIn, skip_none=True)
    @ns.doc(responses={
        200: 'Success',
        401: 'Username or password does not match'
    })
    @ns.doc(security=[])
    def post(self):
        """To Login in"""
        parser = get_login_parser()
        data = parser.parse_args()

        return service.login_user(data=data)

@ns.route('/refresh')
class UserLoginRefresh(Resource):
    @jwt_refresh_token_required
    @ns.marshal_with(dto.authRefresh, skip_none=True)
    def post(self):
        """To get a refresh token"""
        return service.get_refresh_token()

@ns.route('/logout')
class UserLogout(Resource):
    @user_required
    @ns.marshal_with(dto.authResponses, skip_none=True)
    @ns.doc(responses={
        200: 'Logout Successfully'
    })
    def post(self):
        """To logout an user"""
        return service.logout_user()
