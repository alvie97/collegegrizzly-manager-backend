from flask_restful          import Resource
from flask                  import request, current_app
from app                    import db
from app.models.College     import College as CollegeModel
import uuid

class Colleges(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get(
            'per_page', current_app.config['COLLEGES_PER_PAGE'], type=int)

        search = request.args.get('search', '', type=str)

        if search:
            query = CollegeModel.query.filter(
                CollegeModel.name.like('%{}%'.format(search)))
        else:
            query = CollegeModel.query

        data = CollegeModel.to_collection_dict(
                query,
                page,
                per_page,
                'colleges')

        return data

    def delete(self):
        data = request.get_json() or {}

        colleges = CollegeModel.query.filter(
            CollegeModel.public_id.in_(data['ids'])).all()

        for college in colleges:
            db.session.delete(college)

        db.session.commit()

        return {'message': 'Colleges deleted'}

    def post(self):
        data = request.get_json() or {}

        college = CollegeModel(public_id=str(uuid.uuid4()).replace('-', ''), **data)

        db.session.add(college)
        db.session.commit()

        return college.to_dict()
