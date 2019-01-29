from flask_restplus import fields
from datetime import datetime, time
from call_records.dto import standardPaginationDtoModel,\
    standardResponseDtoModel

class TimeField(fields.Raw):
    def format(self, value):
        if isinstance(value, time):
            return value.strftime("%H:%M")
        else:
            return str(value)

class CallChargeDto(object):

    def __init__(self, namespace):
        self.ns = namespace

        self.callcharge = self.ns.model('callcharge', {
            'charge_id': fields.Integer(description='CallCharge identifier'),
            'from_time': TimeField(description='Billing start time'),
            'to_time': TimeField(description='Billing end time'),
            'standing_charge': fields.Float(description='Fixed charges that ' +
                                            'are used to pay for the cost of' +
                                            ' the connection'),
            'minute_charge': fields.Float(description='Charge applies to each' +
                                          ' completed 60 seconds cycle'),
            'date_created': fields.DateTime(
                description='Datetime of call creation'),
            'date_modified': fields.DateTime(
                description='Datetime of call modification'),
        })
        self.callChargeList = self.ns.clone(
            'callChargeList', standardPaginationDtoModel, {
                'results': fields.List(fields.Nested(self.callcharge,
                                                     skip_none=False))
            })
        self.callChargeResponses = self.ns.clone(
            'callChargeResponses', standardResponseDtoModel, {})
