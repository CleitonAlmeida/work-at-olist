from flask_restplus import Namespace, fields
from call_records.dto import standardPaginationDtoModel, standardResponseDtoModel

class CallDto(object):

    def __init__(self, namespace):
        self.ns = namespace

        self.call = self.ns.model('call', {
            'call_id': fields.Integer(description='Call identifier'),
            'source_number': fields.String(description='Origin number of call'),
            'destination_number': fields.String(description='Destination number of call'),
            'initial_timestamp': fields.DateTime(required=False, description='Initial Timestamp'),
            'end_timestamp': fields.DateTime(required=False, description='Final Timestamp'),
            'date_created': fields.DateTime(description='Datetime of call creation'),
            'date_modified': fields.DateTime(description='Datetime of call modification'),
        })
        self.callList = self.ns.clone('callList', standardPaginationDtoModel, {
            'results': fields.List(fields.Nested(self.call, skip_none=False))
        })
        self.callResponses = self.ns.clone('callResponses', standardResponseDtoModel, {})
