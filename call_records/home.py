from flask import Blueprint, jsonify
from flask import current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
bp = Blueprint('home', __name__, url_prefix='/')

import os

@bp.route('/hello')
def hello_world():
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    current_app.logger.info('port %s', port)
    current_app.logger.info('host %s', host)
    current_user = get_jwt_identity()
    current_app.logger.info('Current User %s', current_user)
    return jsonify(hello='Hello World')
