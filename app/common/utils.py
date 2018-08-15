from uuid import uuid4
from app.models.college import College
from app.models.scholarship import Scholarship


def generate_public_id():
  return str(uuid4()).replace('-', '')


def get_college(f):

  def f_wrapper(*args, **kwargs):
    college = College.query.filter_by(public_id=kwargs["college_id"]).first()
    if college is None:
      return {"message": "No college found"}, 404

    return f(college=college, *args, **kwargs)

  return f_wrapper


def get_entity(f):

  def f_wrapper(*args, **kwargs):
    if args[0].entity is College:
      college = College.query.filter_by(public_id=kwargs["entity_id"]).first()
      if college is None:
        return {"message": "No college found"}, 404

      return f(entity=college, *args, **kwargs)
    else:
      scholarship = Scholarship.query.filter_by(
          public_id=kwargs["entity_id"]).first()
      if scholarship is None:
        return {"message": "No scholarship found"}, 404

      return f(entity=scholarship, *args, **kwargs)

  return f_wrapper
