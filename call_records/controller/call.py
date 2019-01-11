from flask import current_app
from flask_restplus import Resource, Namespace
from flask_restplus import reqparse

from call_records.controller import user_required
from call_records.dto.call import CallDto
from call_records.service.call import CallService

service = CallService()
ns = Namespace('call', description='Call')
dto = CallDto(ns)

callDtoModel = dto.call
callListDtoModel = dto.callList
callResponseDtoModel = dto.callResponses

def get_parser_pagination():
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=int, required=False, default=1)
    parser.add_argument('limit', type=int, required=False)
    return parser

@ns.route('/')
class Call(Resource):
    @user_required
    @ns.expect(get_parser_pagination(), validate=True)
    @ns.marshal_list_with(callListDtoModel, envelope='data', skip_none=True)
    def get(self, page=None):
        """List all registered calls"""
        parser = get_parser_pagination()
        data = parser.parse_args()
        return service.get_calls(paginated=True, start=data.get('start'), limit=data.get('limit'))
