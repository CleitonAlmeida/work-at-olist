from flask_restplus import fields
from call_records.dto import standardResponseDtoModel


class AuthDto(object):

    def __init__(self, namespace):
        self.ns = namespace

        self.authLogIn = self.ns.clone('authLogIn', standardResponseDtoModel, {
            'access_token': fields.String(required=False,
                                          description='Token ' +
                                          'used to access protected resources',
                                          example='eyJ0eXAiOiJKV1QiLCJhbGciOiJ'+
                                          'IUzI1NiJ9.eyJpYXQiOjE1NDQ3MjE2MDAsI'+
                                          'm5iZiI6MTU0NDcyMTYwMCwianRpIjoiZjQ3'+
                                          'NTBmMjEtMWExMS00YWExLWI2YTYtMz.argP'+
                                          '9jSHhZ7xWSzFAf1hWHIq6MjpoZb_hTDzUl5'+
                                          'uGUc'),
            'refresh_token': fields.String(required=False,
                                           description='Token used to access '+
                                           'protected resources',
                                           example='eyJ0eXAiOiJKV1QiLCJhbGciOi'+
                                           'JIUzI1NiJ9.eyJ1c2VySWQiOiJiMDhmODZ'+
                                           'hZi0zNWRhLTQ4ZjItOGZhYi1jZWYzOTA0N'+
                                           'jYwYmQifQ.-xN_h82PHVTCMA9vdoHrcZx' +
                                           'H-x5mb11y1537t3rGzcM')
        })

        self.authRefresh = self.ns.model('authRefresh', {
            'status': fields.String(required=True,
                                    enum=('success', 'fail'),
                                    description='Status of refresh token '+
                                    'operation'),
            'access_token': fields.String(required=False,
                                          description='Token used to access '+
                                          'protected resources',
                                          example='eyJ0eXAiOiJKV1QiLCJhbGciOiJ'+
                                          'IUzI1NiJ9.eyJpYXQiOjE1NDQ3MjE2MDAsI'+
                                          'm5iZiI6MTU0NDcyMTYwMCwianRpIjoiZjQ3'+
                                          'NTBmMjEtMWExMS00YWExLWI2YTYtMz.argP'+
                                          '9jSHhZ7xWSzFAf1hWHIq6MjpoZb_hTDzUl5'+
                                          'uGUc')
        })

        self.authResponses = self.ns.clone(
            'authResponses', standardResponseDtoModel, {})
