from flask import Blueprint, jsonify

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('/')
def hello_world():
    return jsonify(hello='Hello World')
