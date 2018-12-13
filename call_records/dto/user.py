from flask_restplus import Namespace, fields


class UserDto:
    ns = Namespace('user', description='User')
    user = ns.model('user', {
        'username': fields.String(required=True, description='User username'),
        'date_created': fields.DateTime(description='Datetime of user creation')
    })
    userLogIn = ns.model('userLogIn', {
        'status': fields.String(required=True, enum=('success', 'fail'), description='Status of login operation'),
        'message': fields.String(required=True, description='An message description', example='Successfully logged in'),
        'access_token': fields.String(required=False, description='Token used to access protected resources', example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDQ3MjE2MDAsIm5iZiI6MTU0NDcyMTYwMCwianRpIjoiZjQ3NTBmMjEtMWExMS00YWExLWI2YTYtMz.argP9jSHhZ7xWSzFAf1hWHIq6MjpoZb_hTDzUl5uGUc')
    })
