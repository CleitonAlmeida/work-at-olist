from functools import wraps
from call_records import fixed
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims
from flask.json import jsonify


def user_required(fn):
    """Here is a custom decorator that verifies the JWT is
    present in the request """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': str(e)
            }
            return response_object, 401
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """Here is a custom decorator that verifies the JWT is
    present in the request, and if the requisitor is admin """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt_claims()
        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': str(e)
            }
            return response_object, 401
        if claims.get('is_admin'):
            return fn(*args, **kwargs)
        else:
            response_object = {
                'status': 'fail',
                'message': fixed.MSG_ONLY_ADMIN
            }
            return response_object, 403
    return wrapper


def page_not_found(e):
    response_object = {
        'status': 'fail',
        'message': fixed.MSG_404
    }
    return jsonify(response_object), 404
