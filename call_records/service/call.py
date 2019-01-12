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
