from flask import current_app
from flask_restplus import Resource
from flask_restplus import reqparse
from flask_jwt_extended import jwt_refresh_token_required, get_raw_jwt

from call_records.controller import user_required
from call_records.dto.auth import AuthDto
from call_records.service.auth import login_user, get_refresh_token, logout_user

ns = AuthDto.ns
authLogInDtoModel = AuthDto.authLogIn
authRefreshDtoModel = AuthDto.authRefresh
authResponsesDtoModel = AuthDto.authResponses


def get_login_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('password', type=str, required=True)
    return parser

@ns.route('/login')
class UserLogin(Resource):
    @ns.expect(get_login_parser(), validate=True)
    @ns.marshal_with(authLogInDtoModel, skip_none=True)
    @ns.doc(responses={
        200: 'Success',
        401: 'Username or password does not match'
    })
    @ns.doc(security=[])
    def post(self):
        """To Login in"""
        parser = get_login_parser()
        data = parser.parse_args()

        return login_user(data=data)

@ns.route('/refresh')
class UserLoginRefresh(Resource):
    @user_required
    @ns.marshal_with(authRefreshDtoModel, skip_none=True)
    #@jwt_refresh_token_required
    def post(self):
        """To get a refresh token"""
        return get_refresh_token()

@ns.route('/logout')
class UserLogout(Resource):
    @user_required
    @ns.marshal_with(authResponsesDtoModel, skip_none=True)
    @ns.doc(responses={
        200: 'Logout Successfully'
    })
    def post(self):
        """To logout an user"""
        return logout_user()
