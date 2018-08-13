from flask_restful import Resource
from flask import request, current_app
from app import db
from app.models.college import College as CollegeModel
from app.models.state import State as StateModel
from app.models.county import County as CountyModel
from app.models.place import Place as PlaceModel
from app.models.consolidated_city import ConsolidatedCity as CCModel
from app.models.major import Major as MajorModel
from app.common.utils import generate_public_id


class College(Resource):

  def get(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()

    if college is None:
      return {'message': 'no college found'}, 404

    return college.to_dict()

  def put(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()

    if college is None:
      return {'message': 'no college found'}, 404

    data = request.get_json() or {}

    college.from_dict({data['key']: data['value']})
    db.session.commit()
    return college.to_dict()


class Colleges(Resource):

  def get(self):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get(
        'per_page', current_app.config['COLLEGES_PER_PAGE'], type=int)

    search = request.args.get('search', '', type=str)

    if search:
      query = CollegeModel.query.filter(
          CollegeModel.name.like('%{}%'.format(search)))

      data = CollegeModel.to_collection_dict(
          query, page, per_page, 'colleges', search=search)
    else:
      query = CollegeModel.query
      data = CollegeModel.to_collection_dict(query, page, per_page, 'colleges')

    return data

  def delete(self):
    data = request.get_json() or {}
    if 'public_id' not in data:
      return {'message': 'no public_id attribute found'}, 404

    college = CollegeModel.query.filter_by(public_id=data['public_id'])
    college.delete()
    db.session.commit()

    return {'message': 'Colleges deleted'}

  def post(self):
    data = request.get_json() or {}

    college = CollegeModel(public_id=generate_public_id(), **data)

    db.session.add(college)
    db.session.commit()

    return college.to_dict()


class InStateRequirement(Resource):

  def get(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()
    if college is None:
      return {"message": "No college found"}, 404

    return college.in_state_requirement()

  def put(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()
    if college is None:
      return {"message": "No college found"}, 404

    in_state_requirement = request.get_json() or {}

    if not in_state_requirement:
      return

    if "states" in in_state_requirement:
      for required_state in in_state_requirement["states"]:
        if not college.has_state(fips_code=required_state["fips_code"]):
          state = StateModel.query.filter_by(
              fips_code=required_state["fips_code"]).first()
          if state is not None:
            college.add_state(state)

    if "counties" in in_state_requirement:
      for required_county in in_state_requirement["counties"]:
        if not college.has_county(fips_code=required_county["fips_code"]):
          county = CountyModel.query.filter_by(
              fips_code=required_county["fips_code"]).first()
          if county is not None:
            college.add_county(county)

    if "places" in in_state_requirement:
      for required_place in in_state_requirement["places"]:
        if not college.has_place(fips_code=required_place["fips_code"]):
          place = PlaceModel.query.filter_by(
              fips_code=required_place["fips_code"]).first()
          if place is not None:
            college.add_place(place)

    if "consolidated_cities" in in_state_requirement:
      for required_consolidated_city in in_state_requirement[
          "consolidated_cities"]:
        if not college.has_consolidated_city(
            fips_code=required_consolidated_city["fips_code"]):
          consolidated_city = CCModel.query.filter_by(
              fips_code=required_consolidated_city["fips_code"]).first()
          if consolidated_city is not None:
            college.add_consolidated_city(consolidated_city)

    return college.in_state_requirement()

  def delete(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()
    if college is None:
      return {"message": "No college found"}, 404

    in_state_requirement = request.get_json() or {}

    if not in_state_requirement:
      return

    if "states" in in_state_requirement:
      for required_state in in_state_requirement["states"]:
        if college.has_state(fips_code=required_state["fips_code"]):
          state = StateModel.query.filter_by(
              fips_code=required_state["fips_code"]).first()
          if state is not None:
            college.remove_state(state)

    if "counties" in in_state_requirement:
      for required_county in in_state_requirement["counties"]:
        if college.has_county(fips_code=required_county["fips_code"]):
          county = CountyModel.query.filter_by(
              fips_code=required_county["fips_code"]).first()
          if county is not None:
            college.remove_county(county)

    if "places" in in_state_requirement:
      for required_place in in_state_requirement["places"]:
        if college.has_place(fips_code=required_place["fips_code"]):
          place = PlaceModel.query.filter_by(
              fips_code=required_place["fips_code"]).first()
          if place is not None:
            college.remove_place(place)

    if "consolidated_cities" in in_state_requirement:
      for required_consolidated_city in in_state_requirement[
          "consolidated_cities"]:
        if college.has_consolidated_city(
            fips_code=required_consolidated_city["fips_code"]):
          consolidated_city = CCModel.query.filter_by(
              fips_code=required_consolidated_city["fips_code"]).first()
          if consolidated_city is not None:
            college.remove_consolidated_city(consolidated_city)

    return college.in_state_requirement()


class Majors(Resource):

  def get(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()
    if college is None:
      return {"message": "No college found"}, 404

    return {"majors": college.majors}

  def put(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()
    if college is None:
      return {"message": "No college found"}, 404

    majors = request.get_json() or {}

    if majors:
      return

    for major in majors:
      if not college.has_major(major):
        new_major = MajorModel.query.filter_by(name=major).first()
        if new_major is None:
          new_major = MajorModel(name=major)
          db.session.add(new_major)
          db.session.commit()
        college.add_major(new_major)

    return {"majors": college.majors}

  def delete(self, college_id):
    college = CollegeModel.query.filter_by(public_id=college_id).first()
    if college is None:
      return {"message": "No college found"}, 404

    majors = request.get_json() or {}

    if majors:
      return

    for major in majors:
      if college.has_major(major):
        major_to_delete = MajorModel.query.filter_by(name=major).first()
        college.remove_major(major_to_delete)

    return {"majors": college.majors}
