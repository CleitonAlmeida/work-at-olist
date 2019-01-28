def check_first_admin_user():
    """
    Verify if exists an user admin, and if not, create
    The system can not be run securely containing the admin password in
    the var ADMIN_PASSWORD then, for safety, this function check this
    and log this event as a warning in log (if necessary).
    """
    from flask import current_app
    from call_records.model.user import User
    from call_records.service.user import UserService
    username = current_app.config.get('ADMIN_USERNAME')
    password = current_app.config.get('ADMIN_PASSWORD')
    service = UserService()
    if username and password:
        user_admin = service.get_a_user(username)
        if not user_admin:
            data = {'username': username,
                    'password': password, 'is_admin': True}
            service.save_user(data)
        if user_admin.verify_password(password=password):
            current_app.logger.warning(
                'The user\'s password remains the same as the one defined in'+
                ' the .env file. For security it is necessary to change it')
