from flask_restful import Resource
from flask import jsonify, request

class Colleges(Resource):
    def get(self):
        return {'message': 'get all colleges'}

    def post(self):
        data = request.get_json()
        return {'message': 'create college data: {}'.format(data)}

class College(Resource):
    def get(self, college_id):
        return {'message': 'show college {}'.format(college_id)}

    def put(self, college_id):
        return {'message': 'update college {}'.format(college_id)}

class Scholarships(Resource):
    def get(self):
        return {'message': 'get all scholarships'}

    def post(self, college_id):
        return {
            'message': 'create new scholarship for college {}'
                            .format(college_id)
        }

class Scholarship(Resource):
    def get(self, scholarship_id):
        return {'message': 'get scholarship {}'.format(scholarship_id)}

    def put(self, scholarship_id):
        return {'message': 'update scholarship {}'.format(scholarship_id)}
