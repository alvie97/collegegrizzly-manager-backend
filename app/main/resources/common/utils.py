from app.models.state import State
from app import db
from flask_restful import Resource
from flask import request
from app.common.utils import get_entity


class StateRequirement(Resource):

  def __init__(self, **kwargs):
    self.entity = kwargs["entity"]

  @get_entity
  def get(self, entity_id, entity):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 15, type=int)

    return {"states": entity.get_states_requirement(page, per_page)}

  @get_entity
  def post(self, entity_id, entity):
    data = request.get_json() or {}

    if data:
      for state_fips in data["states_fips"]:
        state = State.query.filter_by(fips_code=state_fips).first()
        print(state)

        if state is not None:
          entity.add_state(state)

    db.session.commit()
    return {"message": "added states to in state requirement"}

  @get_entity
  def delete(self, entity_id, entity):
    data = request.get_json() or {}

    if data:
      for state_fips in data["states_fips"]:
        state = State.query.filter_by(fips_code=state_fips).first()

        if state is not None:
          entity.remove_state(state)

    db.session.commit()
    return {"message": "removed states to in state requirement"}
