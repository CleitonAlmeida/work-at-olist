from call_records.model.call import Call
from call_records.service.util import paginated_list
from call_records import fixed
from flask import request, current_app
from sqlalchemy import between, or_, and_
from sqlalchemy.orm import exc as sa_exc
from call_records import db


class CallService(object):

    def get_calls(self, paginated=False, start=None, limit=None):
        if paginated:
            return paginated_list(Call, request.base_url,
                                  start=start, limit=limit)
        else:
            return Call.query.all()

    def get_a_call(self, call_id):
        call = Call.query.filter_by(call_id=call_id).first()
        if call:
            return call
        else:
            return {}, 404

    def update_call(self, call_id, data):
        try:
            call = Call.query.filter(Call.call_id == call_id).one()
        except sa_exc.NoResultFound as e:
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_CALL_NOT_FOUND
            }
            return response_object, 404

        if data['type'] == 'start':
            call.initial_timestamp = data['timestamp']
            call.source_number = data['source']
            call.destination_number = data['destination']
        else:
            call.end_timestamp = data['timestamp']
        if not self.__valid_call_period(call):
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_CONFLICT_CALLS
            }
            return response_object, 409

        call.save()
        response_object = {
            'status': 'success',
            'message': fixed.MSG_SUCCESSFULLY_UPDATED
        }
        return response_object, 200

    def save_call(self, data):
        try:
            filters = (
                Call.call_id == data['call_id'],
            )
            call = Call.query.filter(*filters).one()
        except sa_exc.NoResultFound:
            call = None

        if call:
            if ((data['type'] == 'start' and call.initial_timestamp is not None)
                    or
                    (data['type'] == 'end' and call.end_timestamp is not None)):
                response_object = {
                    'status': 'fail',
                    'message': fixed.MSG_ACTION_NOT_ALLOWED
                }
                return response_object, 405

        elif call is None:
            call = Call(
                call_id=data['call_id']
            )
        if data['type'] == 'start':
            call.initial_timestamp = data['timestamp']
            call.source_number = data['source']
            call.destination_number = data['destination']
        else:
            call.end_timestamp = data['timestamp']

        if not self.__valid_call_period(call):
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_CONFLICT_CALLS
            }
            return response_object, 409

        call.save()
        response_object = {
            'status': 'success',
            'message': fixed.MSG_SUCCESSFULLY_REGISTRED
        }
        return response_object, 201

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

    def __valid_call_period(self, call):
        if call.initial_timestamp is not None and\
                call.end_timestamp is not None:
            if call.initial_timestamp >= call.end_timestamp:
                return False

        query = Call.query.filter(
            and_(
                Call.initial_timestamp != None,
                Call.end_timestamp != None
            )
        ).filter(
            or_(
                or_(Call.source_number == str(call.destination_number),
                    Call.destination_number == str(call.source_number)
                    ),
                or_(Call.source_number == str(call.source_number),
                    Call.destination_number == str(call.destination_number)
                    )
            )
        )
        if call.initial_timestamp is not None\
                and call.end_timestamp is not None:
            query = query.filter(
                or_(
                    or_(
                        and_(
                            Call.initial_timestamp >= call.initial_timestamp,
                            Call.initial_timestamp <= call.end_timestamp
                        ),
                        and_(
                            Call.end_timestamp >= call.initial_timestamp,
                            Call.end_timestamp <= call.end_timestamp
                        ),
                    ),
                    and_(
                        Call.initial_timestamp <= call.initial_timestamp,
                        Call.end_timestamp >= call.end_timestamp
                    ),
                )
            )
        elif call.initial_timestamp is not None:
            query = query.filter(
                and_(
                    Call.initial_timestamp <= call.initial_timestamp,
                    Call.end_timestamp >= call.initial_timestamp
                )
            )
        else:
            query = query.filter(
                and_(
                    Call.initial_timestamp <= call.end_timestamp,
                    Call.end_timestamp >= call.end_timestamp
                )
            )
        if call.id is not None:
            query = query.filter(Call.call_id != call.call_id)
        #current_app.logger.info('Query %s', str(query))

        _result = query.first()
        if _result is not None:
            return False
        return True
