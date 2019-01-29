from flask import current_app, request
from flask_restplus import Resource, Namespace
from flask_restplus import reqparse
from call_records.controller import admin_required
from call_records.dto.callcharge import CallChargeDto
from call_records.service.callcharge import CallChargeService
from call_records import fixed
from datetime import datetime
from decimal import Decimal

service = CallChargeService()
ns = Namespace('callcharge', description='Call Charge')
dto = CallChargeDto(ns)


def get_parser_pagination():
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=int, required=False, default=1,
                        help='The position from which the data will be' +
                        ' returned')
    parser.add_argument('limit', type=int, required=False,
                        help='The max number of items to return from the' +
                        ' current position')
    return parser


def get_callcharge_parser():
    parser = reqparse.RequestParser()
    parser.add_argument('charge_id',
                        type=int,
                        required=True,
                        help='CallCharge identifier. Unique for each call' +
                        ' charge record')
    parser.add_argument('from_time',
                        type=lambda x: datetime.strptime(x,
                                                         '%H:%M').time(),
                        required=True,
                        help='from_time'
                        )
    parser.add_argument('to_time',
                        type=lambda x: datetime.strptime(x,
                                                         '%H:%M').time(),
                        required=True,
                        help='to_time'
                        )
    parser.add_argument('standing_charge',
                        type=lambda x: Decimal(float(x)),
                        required=True,
                        help='standing_charge'
                        )
    parser.add_argument('minute_charge',
                        type=lambda x: Decimal(float(x)),
                        required=True,
                        help='minute_charge'
                        )
    return parser


@ns.route('/')
class CallCharge(Resource):
    @admin_required
    @ns.expect(get_parser_pagination(), validate=True)
    @ns.marshal_list_with(dto.callChargeList, envelope='data', skip_none=True)
    def get(self, page=None):
        """List all registered callcharges"""
        parser = get_parser_pagination()
        data = parser.parse_args()
        return service.get_callcharges(
            paginated=True,
            start=data.get('start'),
            limit=data.get('limit'))

    @admin_required
    @ns.expect(get_callcharge_parser(), validate=True)
    @ns.marshal_with(dto.callChargeResponses)
    def post(self):
        """To create a new callcharge registry"""
        parser = get_callcharge_parser()
        data = parser.parse_args()
        return service.save_callcharge(data=data)
