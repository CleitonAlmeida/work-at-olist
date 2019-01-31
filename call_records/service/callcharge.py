from call_records.model.callcharge import CallCharge
from call_records.service.util import paginated_list
from call_records import fixed
from flask import request, current_app
from sqlalchemy.orm import exc as sa_exc
from sqlalchemy import or_, and_
from call_records import db
from datetime import datetime, time


class CallChargeService(object):

    def __valid_callcharge_period(self, callcharge):
        if callcharge.from_time >= callcharge.to_time:
            return False

        if callcharge.from_time >= time(0) and \
                callcharge.to_time <= time(23, 59):
            query = CallCharge.query.filter(
                or_(
                    or_(
                        and_(
                            CallCharge.from_time >= callcharge.from_time,
                            CallCharge.from_time <= callcharge.to_time
                        ),
                        and_(
                            CallCharge.to_time >= callcharge.from_time,
                            CallCharge.to_time <= callcharge.to_time
                        ),
                    ),
                    and_(
                        CallCharge.from_time <= callcharge.from_time,
                        CallCharge.to_time >= callcharge.to_time
                    ),
                )
            )

            if callcharge.id is not None:
                query = query.filter(CallCharge.charge_id !=
                                     callcharge.charge_id)

            _result = query.first()
            if _result is None:
                return True
        return False

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
        else:
            callcharge = CallCharge()
            callcharge.charge_id = data['charge_id']
            callcharge.from_time = data['from_time']
            callcharge.to_time = data['to_time']
            callcharge.standing_charge = data['standing_charge']
            callcharge.minute_charge = data['minute_charge']

            if not self.__valid_callcharge_period(callcharge):
                response_object = {
                    'status': 'fail',
                    'message': fixed.MSG_CONFLICT_CALL_CHARGER
                }
                return response_object, 409
            else:
                callcharge.save()
                response_object = {
                    'status': 'success',
                    'message': fixed.MSG_SUCCESSFULLY_REGISTRED
                }
                return response_object, 201

    def update_callcharge(self, charge_id, data):
        try:
            callcharge = CallCharge.query.filter(
                CallCharge.charge_id == charge_id
            ).one()
        except sa_exc.NoResultFound as e:
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_CALL_CHARGER_NOT_FOUND
            }
            return response_object, 404

        callcharge.from_time = data['from_time']
        callcharge.to_time = data['to_time']
        callcharge.standing_charge = data['standing_charge']
        callcharge.minute_charge = data['minute_charge']

        if not self.__valid_callcharge_period(callcharge):
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_CONFLICT_CALL_CHARGER
            }
            return response_object, 409
        else:
            callcharge.save()
            response_object = {
                'status': 'success',
                'message': fixed.MSG_SUCCESSFULLY_UPDATED
            }
            return response_object, 200

    def get_callcharges(self, paginated=False, start=None, limit=None):
        if paginated:
            return paginated_list(CallCharge, request.base_url,
                                  start=start, limit=limit)
        else:
            return CallCharge.query.all()

    def get_a_callcharge(self, charge_id):
        callcharge = CallCharge.query.filter_by(charge_id=charge_id).first()
        return callcharge

    def delete_a_callcharge(self, charge_id):
        try:
            callcharge = CallCharge.query.filter_by(charge_id=charge_id).first()
            if callcharge:
                callcharge.delete()
                return True
            else:
                return False
        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': e
            }
            return response_object, 500
