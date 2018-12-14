from functools import wraps
from flask_jwt_extended import verify_jwt_in_request

# Here is a custom decorator that verifies the JWT is present in the request
def user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            response_object = {
                'status': 'fail',
                'message': str(e)
            }
            return response_object, 401
    return wrapper
