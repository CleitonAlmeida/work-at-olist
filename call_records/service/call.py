from call_records.model.call import Call
from call_records.service.util import paginated_list
from flask import request

class CallService(object):

    def get_calls(self, paginated=False, start=None, limit=None):
        if paginated:
            return paginated_list(Call, request.base_url,\
                start=start, limit=limit)
        else:
            return Call.query.all()

    def get_a_call(self, call_id):
        call = Call.query.filter_by(call_id=call_id).first()
        if call:
            return call
        else:
            return {}, 404

    def delete_a_call(self, call_id):
        try:
            call = Call.query.filter_by(call_id=call_id).first()
            if call:
                call.delete()
                return True
            else:
                return False
        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': e
            }
            return response_object, 500
