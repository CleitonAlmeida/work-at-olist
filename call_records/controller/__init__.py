from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims

# Here is a custom decorator that verifies the JWT is present in the request
def user_required(fn):
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
                'message': 'You must be admin'
            }
            return response_object, 403
    return wrapper
