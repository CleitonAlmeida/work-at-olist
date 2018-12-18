def save_changes(data):
    from call_records import db
    db.session.add(data)
    db.session.commit()

def save_new_user(data):
    from call_records.model.user import User
    from flask import current_app

    user = User.query.filter_by(username=data['username']).first()
    if not user:
        new_user = User(
            username = data['username'],
            password_hash = data['password'],
            is_admin = data.get('is_admin', False)
        )
        new_user.gen_hash(data['password'])
        save_changes(new_user)
        response_object = {
            'status': 'success',
            'message': 'Successfully registered'
        }
        return response_object, 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please Log in',
        }
        return response_object, 409

def get_a_user(username):
    from call_records.model.user import User
    return User.query.filter_by(username=username).first()

def get_a_user_or_admin(username):
    from call_records.model.user import User
    return User.query.filter((User.username==username) | (User.is_admin==True)).first()

def get_all_users():
    from call_records.model.user import User
    return User.query.all()

def login_user(data):
    from call_records.model.user import User
    from flask import current_app
    from flask_jwt_extended import (
        JWTManager, jwt_required, create_access_token,
        get_jwt_identity
    )

    try:
        user = User.query.filter_by(username=data.get('username')).first()
        if user and user.verify_password(password=data.get('password')):
            access_token = create_access_token(identity=data.get('username'))
            response_object = {
                'status': 'success',
                'message': 'Successfully logged in',
                'access_token': access_token
            }
            return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'Username or password does not match.'
            }
            return response_object, 401
    except Exception as e:
        current_app.logger.warning('ERROR Login %s', e)
        response_object = {
            'status': 'fail',
            'message': 'Try again'
        }
        return response_object, 500
