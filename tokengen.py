from models import Users
from flask import jsonify, request
import jwt
from datetime import datetime, timedelta
from functools import wraps
from config import app

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        print(token)
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
    return decorated



def gen_token(username):
    print(username)
    username = Users.query.filter_by(username=username).first().username
    token = jwt.encode({'username': username, 'exp': datetime.utcnow() + timedelta(minutes=40)},app.config['SECRET_KEY'])
    return token 

def genrate_token(username):
    username = Users.query.filter_by(Username=username).first().Username
    token = jwt.encode({'username': username, 'exp': datetime.utcnow() + timedelta(minutes=40)},app.config['SECRET_KEY'])
    return token 
