from flask_restplus import fields
from flask_restplus import Model
from flask import current_app

standardResponseDtoModel = Model('standardResponse', {
    'status': fields.String(required=True, enum=('success', 'fail'), description='Status of operation'),
    'message': fields.String(required=True, description='Message describing the success of the operation or the reason for an error')
})

standardPaginationDtoModel = Model('standardPagination', {
    'start': fields.Integer(required=True, description='It is the position from which we want the data to be returned'),
    'limit': fields.Integer(required=True, description='It is the max number of items to return from that position'),
    'next': fields.String(required=False, description='It is the url for the next page of the query assuming current value of limit'),
    'previous': fields.String(required=False, description='It is the url for the previous page of the query assuming current value of limit')
})
