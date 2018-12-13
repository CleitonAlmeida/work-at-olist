from flask_restplus import Namespace, fields


class UserDto:
    ns = Namespace('user', description='user')
    user = ns.model('user', {
        'username': fields.String(required=True, description='user username'),
        'date_created': fields.DateTime(description='datetime of user creation')
    })
