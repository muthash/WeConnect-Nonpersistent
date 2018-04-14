from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import get_raw_jwt, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from app.models import User
# from app.utils import (
#     validate_null, random_string, send_reset_password, messages
# )
from app.baseview import BaseView

auth = Blueprint('auth', __name__, url_prefix='/api/v1')
users = []
blacklist = set()


class RegisterUser(BaseView):
    """Method to Register a new user"""
    def post(self):
        """Endpoint to save the data to the database"""
        if not self.validate_json():
            data = request.get_json()
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            user_data = {'email': email, 'username': username,
                        'password': password}
            if not self.validate_null(**user_data):
                if not self.check_email(email):
                    emails = [user.email for user in users]
                    if email not in emails:
                        user = User(email, username, password)
                        users.append(user)
                        response = {'message': 'Account created successfully'}
                        return jsonify(response), 201
                    response = {'message': 'User already exists. Please login'}
                    return jsonify(response), 409
                return self.check_email(email)
            return self.validate_null(**user_data)
        return self.validate_json()


class LoginUser(BaseView):
    """Method to Login a user"""
    def post(self):
        """Endpoint to save the data to the database"""
        if not self.validate_json():
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            user_data = {'email': email, 'password': password}
            if not self.validate_null(**user_data):
                user_ = [user for user in users if email == user.email]
                if user_:
                    user = user_[0]
                    if Bcrypt().check_password_hash(user.password, password):
                        return self.generate_token(user.email, user.username)
                    response = {'message': 'Invalid email or password'}
                    return jsonify(response), 401
                response = {'message': 'Invalid email or password'}
                return jsonify(response), 401
            return self.validate_null(**user_data)
        return self.validate_json()


class LogoutUser(MethodView):
    """Method to logout a user"""
    @jwt_required
    def post(self):
        """Endpoint to logout a user"""
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        response = {'message': 'Successfully logged out'}
        return jsonify(response), 200


auth.add_url_rule('/register', view_func=RegisterUser.as_view('register'))
auth.add_url_rule('/login', view_func=LoginUser.as_view('login'))
auth.add_url_rule('/logout', view_func=LogoutUser.as_view('logout'))
