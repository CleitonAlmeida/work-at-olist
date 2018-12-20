from flask_restplus import Namespace, fields


class UserDto:
    ns = Namespace('user', description='User')
    user = ns.model('user', {
        'username': fields.String(required=True, description='User username'),
        'date_created': fields.DateTime(description='Datetime of user creation'),
        'date_modified': fields.DateTime(description='Datetime of user modification'),
        'is_admin': fields.Boolean(description='Role of user (if is admin or not admin)')
    })
    userList = ns.model('userList', {
        'start': fields.Integer(required=True, description='It is the position from which we want the data to be returned'),
        'limit': fields.Integer(required=True, description='It is the max number of items to return from that position'),
        'next': fields.String(required=False, description='It is the url for the next page of the query assuming current value of limit'),
        'previous': fields.String(required=False, description='It is the url for the previous page of the query assuming current value of limit'),
        'results': fields.List(fields.Nested(user, skip_none=True))
    })
    userLogIn = ns.model('userLogIn', {
        'status': fields.String(required=True, enum=('success', 'fail'), description='Status of login operation'),
        'message': fields.String(required=True, description='An message description', example='Successfully logged in'),
        'access_token': fields.String(required=False, description='Token used to access protected resources', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDQ3MjE2MDAsIm5iZiI6MTU0NDcyMTYwMCwianRpIjoiZjQ3NTBmMjEtMWExMS00YWExLWI2YTYtMz.argP9jSHhZ7xWSzFAf1hWHIq6MjpoZb_hTDzUl5uGUc')
    })
    userRefresh = ns.model('userRefresh', {
        'status': fields.String(required=True, enum=('success', 'fail'), description='Status of refresh token operation'),
        'access_token': fields.String(required=False, description='Token used to access protected resources', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDQ3MjE2MDAsIm5iZiI6MTU0NDcyMTYwMCwianRpIjoiZjQ3NTBmMjEtMWExMS00YWExLWI2YTYtMz.argP9jSHhZ7xWSzFAf1hWHIq6MjpoZb_hTDzUl5uGUc')
    })
    userResponses = ns.model('userResponses', {
        'status': fields.String(required=True, enum=('success', 'fail'), description='Status of operation'),
        'message': fields.String(required=True, description='Message describing the success of the operation or the reason for an error')
    })
