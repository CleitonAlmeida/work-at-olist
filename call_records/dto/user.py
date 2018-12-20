from flask_restplus import Namespace, fields
from call_records.dto import standardPaginationDtoModel, standardResponseDtoModel

class UserDto:
    ns = Namespace('user', description='User')
    user = ns.model('user', {
        'username': fields.String(required=True, description='User username'),
        'date_created': fields.DateTime(description='Datetime of user creation'),
        'date_modified': fields.DateTime(description='Datetime of user modification'),
        'is_admin': fields.Boolean(description='Role of user (if is admin or not admin)')
    })
    userList = ns.clone('userList', standardPaginationDtoModel, {
        'results': fields.List(fields.Nested(user, skip_none=True))
    })
    userResponses = ns.clone('userResponses', standardResponseDtoModel, {})
