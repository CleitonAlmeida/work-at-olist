from call_records.model.callcharge import CallCharge
from call_records.service.util import paginated_list
from call_records import fixed
from flask import request, current_app
from sqlalchemy.orm import exc as sa_exc
from call_records import db


class CallChargeService(object):

    def save_callcharge(self, data):
        try:
            filters = (
                CallCharge.charge_id == data['charge_id'],
            )
            callcharge = CallCharge.query.filter(*filters).one()
        except sa_exc.NoResultFound:
            callcharge = None

        if callcharge:
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_ACTION_NOT_ALLOWED
            }
            return response_object, 405
        elif callcharge is None:
            callcharge = CallCharge()
            callcharge.charge_id = data['charge_id']
            callcharge.from_time = data['from_time']
            callcharge.to_time = data['to_time']
            callcharge.standing_charge = data['standing_charge']
            callcharge.minute_charge = data['minute_charge']

            callcharge.save()
            response_object = {
                'status': 'success',
                'message': fixed.MSG_SUCCESSFULLY_REGISTRED
            }
            return response_object, 201

    def get_callcharges(self, paginated=False, start=None, limit=None):
        if paginated:
            return paginated_list(CallCharge, request.base_url,
                                  start=start, limit=limit)
        else:
            return CallCharge.query.all()
