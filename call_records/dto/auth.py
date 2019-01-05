from flask_restplus import Namespace, fields
from call_records.dto import standardResponseDtoModel


class AuthDto:
    ns = Namespace('auth', description='Auth')
    authLogIn = ns.clone('authLogIn', standardResponseDtoModel, {
        'access_token': fields.String(required=False, description='Token used to access protected resources', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDQ3MjE2MDAsIm5iZiI6MTU0NDcyMTYwMCwianRpIjoiZjQ3NTBmMjEtMWExMS00YWExLWI2YTYtMz.argP9jSHhZ7xWSzFAf1hWHIq6MjpoZb_hTDzUl5uGUc'),
        'refresh_token': fields.String(required=False, description='Token used to access protected resources', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiJiMDhmODZhZi0zNWRhLTQ4ZjItOGZhYi1jZWYzOTA0NjYwYmQifQ.-xN_h82PHVTCMA9vdoHrcZxH-x5mb11y1537t3rGzcM')
    })
    authRefresh = ns.model('authRefresh', {
        'status': fields.String(required=True, enum=('success', 'fail'), description='Status of refresh token operation'),
        'access_token': fields.String(required=False, description='Token used to access protected resources', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDQ3MjE2MDAsIm5iZiI6MTU0NDcyMTYwMCwianRpIjoiZjQ3NTBmMjEtMWExMS00YWExLWI2YTYtMz.argP9jSHhZ7xWSzFAf1hWHIq6MjpoZb_hTDzUl5uGUc')
    })
    authResponses = ns.clone('authResponses', standardResponseDtoModel, {})
