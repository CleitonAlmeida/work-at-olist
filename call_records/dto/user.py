from flask_restplus import Namespace, fields


class UserDto:
    api = Namespace('user', description='user')
    user = api.model('user', {
        'username': fields.String(required=True, description='user username'),
        'date_created': fields.DateTime(description='datetime of user creation')
    })
