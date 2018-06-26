from flask import request, jsonify
from app import db
from app.auth import bp
from app.models import User

"""
1. find user
2. generate jwt and send response with user data / send auth error
"""
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.authenticate(data)

    if user is None:
        return jsonify({
            'message'
        }), 401
