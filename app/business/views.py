"""Contains views to register, login reset password and logout user"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_optional
from flask_bcrypt import Bcrypt
from app.models import Business
from app.baseview import BaseView
from app.auth.views import users

biz = Blueprint('biz', __name__, url_prefix='/api/v1/businesses')
rev = Blueprint('rev', __name__,
                url_prefix='/api/v1/businesses/<int:business_id>/reviews')
store = []


class BusinessManipulation(BaseView):
    """Method to manipulate business endpoints"""
    @jwt_required
    def post(self):
        if self.validate_json():
            return self.validate_json()
        data = request.get_json()
        name = data.get('name')
        category = data.get('category')
        location = data.get('location')
        current_user = get_jwt_identity()
        data_ = dict(name=name, category=category, location=location)

        if self.validate_null(**data_):
            return self.validate_null(**data_)

        user_ = [user for user in users if current_user == user.email]
        if not user_:
            response = {'message': 'Login in to register business'}
            return jsonify(response), 401

        data = self.remove_extra_spaces(**data_)
        available = [business for business in store if data['name'] == business.name]
        if available:
            name = data['name']
            response = {'message': f'Business with name {name} already exists'}
            return jsonify(response), 409

        business = Business(**data, created_by=current_user)
        store.append(business)
        response = {'message': 'Business with name {} created'.format(name)}
        return jsonify(response), 201

    @jwt_required
    def put(self, business_id):
        """update a single business"""
        if self.validate_json():
            return self.validate_json()
        data = request.get_json()
        name = data.get('name')
        category = data.get('category')
        location = data.get('location')
        current_user = get_jwt_identity()
        data_ = dict(name=name, category=category, location=location)
        if self.validate_null(**data_):
            return self.validate_null(**data_)
        business_ = [business for business in store
                     if business_id == business.id]
        if not business_:
            response = {'message': f'The business with id {business_id}' +
                        ' is not available'}
            return jsonify(response), 404
        index = store.index(business_[0])
        if current_user != store[index].created_by:
            response = {'message': 'The operation is forbidden' +
                        ' for this business'}
            return jsonify(response), 403
        data = self.remove_extra_spaces(**data_)
        store[index].name = data['name']
        store[index].category = data['category']
        store[index].location = data['location']
        response = {'message': 'Business updated successfully'}
        return jsonify(response), 200

    @jwt_required
    def delete(self, business_id):
        if self.validate_json():
            return self.validate_json()
        data = request.get_json()
        password = data.get('password')
        current_user = get_jwt_identity()
        data_ = dict(password=password)
        if self.validate_null(**data_):
            return self.validate_null(**data_)

        user_ = [user for user in users if current_user == user.email]
        if not user_:
            response = {'message': 'Please login to delete business'}
            return jsonify(response), 401

        user = user_[0]
        if not Bcrypt().check_password_hash(user.password, password):
            response = {'message': 'Enter correct password to delete'}
            return jsonify(response), 401

        business_ = [business for business in store
                     if business_id == business.id]
        if not business_:
            response = {'message': f'The business with id {business_id}' +
                                   ' is not available'}
            return jsonify(response), 404

        index = store.index(business_[0])
        if current_user != store[index].created_by:
            response = {'message': 'The operation is forbidden' +
                                   ' for this business'}
            return jsonify(response), 403
        del store[index]
        response = {'message': f'Business with id {business_id} deleted'}
        return jsonify(response), 200

    @jwt_optional
    def get(self, business_id):
        """return a list of all businesses else a single business"""
        filter_by = request.args.get('category', 'all', type=str)
        if business_id is None and filter_by == "all":
            business_ = [business.serialize() for business in store]
            if business_:
                response = {'businesses': business_}
                return jsonify(response), 200
            response = {'message': 'There are no businesses registered' +
                                   ' currently'}
            return jsonify(response), 202
        if business_id is None and filter_by != "all":
            business_ = [business.serialize() for business in store
                        if filter_by == business.category]
            if business_:
                response = {'businesses': business_}
                return jsonify(response), 200
            response = {'message': 'There are no businesses registered' +
                                   f' in {filter_by} category'}
            return jsonify(response), 202
        if business_id is not None:
            business_ = [business.serialize() for business in store
                         if business_id == business.id]
            if business_:
                response = {'businesses': business_}
                return jsonify(response), 200
            response = {'message': f'The business with id {business_id}' +
                                   ' is not available'}
            return jsonify(response), 404


class ReviewManipulation(BaseView):
    """Method to manipulate business endpoints"""
    @jwt_required
    def post(self, business_id):
        """Endpoint to save the data to the database"""
        if self.validate_json():
            return self.validate_json()

        data = request.get_json()
        review = data.get('review')
        current_user = get_jwt_identity()
        data_ = dict(review=review)

        if self.validate_null(**data_):
            return self.validate_null(**data_)

        business_ = [business for business in store
                     if business_id == business.id]
        if not business_:
            response = {'message': f'The business with id {business_id}' +
                                   ' is not available'}
            return jsonify(response), 404

        business = business_[0]
        index = store.index(business_[0])
        if current_user == business.created_by:
            response = {'message': 'The operation is forbidden for' +
                                   ' own business'}
            return jsonify(response), 403
        data = self.remove_extra_spaces(**data_)
        store[index].reviews.append(data['review'])
        response = {'message': 'Review for business with id' +
                               f' {business_id} created'}
        return jsonify(response), 201


business_view = BusinessManipulation.as_view('businesses')
biz.add_url_rule('', defaults={'business_id': None},
                 view_func=business_view, methods=['GET', ])
biz.add_url_rule('', view_func=business_view, methods=['POST', ])
biz.add_url_rule('/<int:business_id>', view_func=business_view,
                 methods=['GET', 'PUT', 'DELETE', ])
biz.add_url_rule('/<int:business_id>/reviews', view_func=business_view,
                 methods=['GET'])

review_view = ReviewManipulation.as_view('reviews')
rev.add_url_rule('', view_func=review_view, methods=['POST'])
