from flask_restful import Resource
from flask import request, current_app

from app import db
from app.models.college import College as CollegeModel
from app.models.scholarship import Scholarship as ScholarshipModel
from app.models.program import Program as ProgramModel
from app.models.ethnicity import Ethnicity as EthnicityModel
from app.common.utils import get_entity, generate_public_id
from app.schemas.scholarship_schema import ScholarshipSchema
from app.schemas.program_schema import ProgramSchema
from app.schemas.ethnicity_schema import EthnicitySchema
from marshmallow import ValidationError

scholarship_schema = ScholarshipSchema()
program_schema = ProgramSchema()
ethnicity_schema = EthnicitySchema()


class Scholarship(Resource):

    @get_entity(ScholarshipModel, "scholarship")
    def get(self, scholarship: ScholarshipModel):

        return {"scholarship": scholarship.to_dict()}

    @get_entity(ScholarshipModel, "scholarship")
    def put(self, scholarship: ScholarshipModel):
        data = request.get_json()

        if not data:
            return {"message": "no data provided"}, 400

        try:
            scholarship_schema.load(data, partial=True)
        except ValidationError as err:
            return err.messages, 422

        scholarship.update(data)
        db.session.commit()
        return {"scholarship": scholarship.to_dict()}

    @get_entity(ScholarshipModel, "scholarship")
    def delete(self, scholarship: ScholarshipModel):

        db.session.delete(scholarship)
        db.session.commit()
        return {"message": "scholarship deleted"}


class Scholarships(Resource):

    def get(self):
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get(
            "per_page", current_app.config["SCHOLARSHIPS_PER_PAGE"], type=int)

        return ScholarshipModel.to_collection_dict(ScholarshipModel.query, page,
                                                   per_page, "scholarships")

    @get_entity(CollegeModel, "college")
    def post(self, college: CollegeModel):
        data = request.get_json()

        if not data:
            return {"message": "no data provided"}, 400

        try:
            scholarship_schema.load(data)
        except ValidationError as err:
            return err.messages, 422

        scholarship = ScholarshipModel(
            public_id=generate_public_id(), college=college, **data)

        db.session.add(scholarship)
        db.session.commit()

        return {"scholarship_id": scholarship.public_id}


class ScholarshipPrograms(Resource):

    @get_entity(ScholarshipModel, "scholarship")
    def get(self, scholarship: ScholarshipModel):
        return {"programs": scholarship.get_programs()}

    @get_entity(ScholarshipModel, "scholarship")
    def post(self, scholarship: ScholarshipModel):
        data = request.get_json() or {}

        if not data or "programs" not in data:
            return {"message": "no data provided"}, 400

        for program in data["programs"]:
            try:
                program_schema.load(program)
            except ValidationError as err:
                return err.messages, 422

            program_to_add = ProgramModel.first(name=program["name"])

            if program_to_add is None:
                program_to_add = ProgramModel(**program)
                db.session.add(program_to_add)

            scholarship.add_program(program_to_add)

        db.session.commit()
        return {"message": "programs added"}

    @get_entity(ScholarshipModel, "scholarship")
    def delete(self, scholarship: ScholarshipModel):
        data = request.get_json() or {}

        if not data or "programs" not in data:
            return {"message": "no data provided"}, 400

        for program in data["programs"]:
            program_to_remove = scholarship.programs.filter_by(
                name=program).first()

            if program_to_remove is None:
                return {"message": scholarship.name + "doesn't have program " + program}, 404

            scholarship.remove_program(program_to_remove)

        db.session.commit()
        return {"message": "programs removed"}


class ScholarshipEthnicities(Resource):

    @get_entity(ScholarshipModel, "scholarship")
    def get(self, scholarship: ScholarshipModel):
        return {"ethnicities": scholarship.get_ethnicities()}

    @get_entity(ScholarshipModel, "scholarship")
    def post(self, scholarship: ScholarshipModel):
        data = request.get_json() or {}

        if not data or "ethnicities" not in data:
            return {"message": "no data provided"}, 400

        for ethnicity in data["ethnicities"]:
            try:
                ethnicity_schema.load(ethnicity)
            except ValidationError as err:
                return err.messages, 422

            ethnicity_to_add = EthnicityModel.first(name=ethnicity["name"])

            if ethnicity_to_add is None:
                ethnicity_to_add = EthnicityModel(**ethnicity)
                db.session.add(ethnicity_to_add)

            scholarship.add_ethnicity(ethnicity_to_add)

        db.session.commit()
        return {"message": "ethnicities added"}

    @get_entity(ScholarshipModel, "scholarship")
    def delete(self, scholarship: ScholarshipModel):
        data = request.get_json() or {}

        if not data or "ethnicities" not in data:
            return {"message": "no data provided"}, 400

        for ethnicity in data["ethnicities"]:
            ethnicity_to_remove = scholarship.ethnicities.filter_by(
                name=ethnicity).first()

            if ethnicity_to_remove is None:
                return {"message": scholarship.name + "doesn't have ethnicity " + ethnicity}, 404

            scholarship.remove_ethnicity(ethnicity_to_remove)

        db.session.commit()
        return {"message": "ethnicities removed"}


class ScholarshipsNeeded(Resource):

    @get_entity(ScholarshipModel, "scholarship")
    def get(self, scholarship: ScholarshipModel):

        return {"scholarships_needed": scholarship.get_scholarships_needed()}

    @get_entity(ScholarshipModel, "scholarship")
    @get_entity(CollegeModel, "college")
    def post(self, scholarship: ScholarshipModel, college: CollegeModel):
        data = request.get_json() or {}

        if not data or "scholarships_needed" not in data:
            return {"message": "no data provided"}, 400

        for scholarship_needed in data["scholarships_needed"]:
            if scholarship_needed == scholarship.public_id:
                continue

            scholarship_to_add = college.scholarships.filter_by(
                public_id=scholarship_needed).first()

            if scholarship_to_add is not None:
                scholarship.add_needed_scholarship(scholarship_to_add)

        db.session.commit()
        return {"message": "needed scholarships added"}

    @get_entity(ScholarshipModel, "scholarship")
    def delete(self, scholarship: ScholarshipModel):
        data = request.get_json() or {}

        if not data or "scholarships_needed" not in data:
            return {"message": "no data provided"}, 400

        for scholarship_needed in data["scholarships_needed"]:
            scholarship_to_remove = scholarship.scholarships_needed.filter_by(
                public_id=scholarship_needed).first()

            if scholarship_to_remove is not None:
                scholarship.remove_needed_scholarship(scholarship_to_remove)

        db.session.commit()
        return {"message": "needed scholarships removed"}
