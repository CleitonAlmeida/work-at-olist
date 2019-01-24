from flask import current_app, request
from flask_restplus import Resource, Namespace
from flask_restplus import reqparse
from datetime import datetime

from call_records.controller import user_required
from call_records.dto.call import CallDto
from call_records.service.call import CallService

service = CallService()
ns = Namespace('call', description='Call')
dto = CallDto(ns)

def get_parser_pagination():
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=int, required=False, default=1)
    parser.add_argument('limit', type=int, required=False)
    return parser

def get_call_parser(type, verb):
    parser = reqparse.RequestParser()
    parser.add_argument('type', type=str, choices=['start', 'end'], required=True)
    parser.add_argument('timestamp', type=lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%SZ'), required=True)
    if type == 'start':
        parser.add_argument('source', type=int, required=True)
        parser.add_argument('destination', type=int, required=True)
    if verb == 'post':
        parser.add_argument('call_id', type=int, required=True)
    return parser

@ns.route('/')
class Call(Resource):
    @user_required
    @ns.expect(get_parser_pagination(), validate=True)
    @ns.marshal_list_with(dto.callList, envelope='data', skip_none=True)
    def get(self, page=None):
        """List all registered calls"""
        parser = get_parser_pagination()
        data = parser.parse_args()
        return service.get_calls(
            paginated=True,
            start=data.get('start'),
            limit=data.get('limit'))

    @user_required
    @ns.expect(get_call_parser('', 'post'), validate=True)
    @ns.marshal_with(dto.callResponses)
    def post(self):
        type = request.form.get('type')
        parser = get_call_parser(type, 'post')
        data = parser.parse_args()
        return service.save_call(data=data)

@ns.route('/<call_id>')
@ns.param('call_id', 'The Call identifier')
@ns.response(404, 'Call not found.')
class CallSpecific(Resource):
    @user_required
    @ns.marshal_with(dto.call, skip_none=True)
    def get(self, call_id):
        """Get a call given its ID"""
        call = service.get_a_call(call_id)
        if not call:
            response_object = {
                'status': 'fail',
                'message': 'Call not found'
            }
            return response_object, 404
        else:
            return call

    @user_required
    @ns.expect(get_call_parser('', 'put'), validate=True)
    @ns.marshal_with(dto.callResponses)
    def put(self, call_id):
        type = request.form.get('type')
        parser = get_call_parser(type, 'put')
        data = parser.parse_args()
        return service.update_call(call_id=call_id, data=data)

    @user_required
    @ns.marshal_with(dto.callResponses)
    def delete(self, call_id):
        """Delete a call given its ID"""
        result = service.delete_a_call(int(call_id))
        if not result:
            response_object = {
                'status': 'fail',
                'message': 'Call not found'
            }
            return response_object, 404
        else:
            response_object = {
                'status': 'success',
                'message': 'Call deleted'
            }
            return response_object, 200
