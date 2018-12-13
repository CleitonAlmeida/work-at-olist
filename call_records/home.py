from flask import Blueprint, jsonify
from flask import current_app
bp = Blueprint('home', __name__, url_prefix='/')

import os

@bp.route('/hello')
def hello_world():
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    current_app.logger.info('port %s', port)
    current_app.logger.info('host %s', host)
    return jsonify(hello='Hello World')
