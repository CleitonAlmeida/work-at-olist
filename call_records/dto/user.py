from flask_restplus import fields
from call_records.dto import standardPaginationDtoModel, standardResponseDtoModel


class UserDto(object):

    def __init__(self, namespace):
        self.ns = namespace

        #selfns = Namespace('user', description='User')
        self.user = self.ns.model('user', {
            'username': fields.String(required=True,
                        description='User username'),
            'date_created': fields.DateTime(
                            description='Datetime of user creation'),
            'date_modified': fields.DateTime(
                            description='Datetime of user modification'),
            'is_admin': fields.Boolean(
                        description='Role of user (if is admin or not admin)')
        })
        self.userList = self.ns.clone('userList', standardPaginationDtoModel, {
            'results': fields.List(fields.Nested(self.user, skip_none=True))
        })
        self.userResponses = self.ns.clone(
            'userResponses', standardResponseDtoModel, {})
