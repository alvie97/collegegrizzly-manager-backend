from flask              import request
from flask_restful      import Resource
from app                import db
from app.models.User    import User as UserModel

class Users(Resource):
    def post(self):
        data = request.get_json()

        user = UserModel(email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        return user.to_dict()

class User(Resource):
    def post(self):
        data = request.get_json()

        user = UserModel.query.filter_by(email=data['email']).first()

        if user is None or not user.check_password(data['password']):
            return {'message': 'invalid credentials'}, 401

        return user.to_dict()

    def put(self):
        data = request.get_json()
        user = UserModel.query.filter_by(email=data['email']).first()

        if user is None:
            return {
                'message': 'no user with email {} was found' \
                    .format(data['email'])
            }

        user.from_dict(data)
        db.session.commit()

        return user.to_dict()
