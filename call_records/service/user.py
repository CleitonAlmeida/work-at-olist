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
            password_hash = data['password']
        )
        new_user.password_hash = new_user.gen_hash(new_user.password_hash)
        save_changes(new_user)
        response_object = {
            'status': 'success',
            'message': 'Successfully registered.'
        }
        return response_object, 201
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return response_object, 409

def get_a_user(username):
    from call_records.model.user import User
    return User.query.filter_by(username=username).first()

def get_all_users():
    from call_records.model.user import User
    return User.query.all()
