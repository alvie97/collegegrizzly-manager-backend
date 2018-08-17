from uuid import uuid4


def generate_public_id():
  return str(uuid4()).replace('-', '')


def get_entity(entity, entity_name):

  def get_entity_decorator(f):

    def f_wrapper(*args, **kwargs):
      entity_obj = entity.query.filter_by(public_id=kwargs[entity_name +
                                                           "_id"]).first()
      if entity_obj is None:
        return {"message": "No entity found"}, 404

      return f(entity_obj=entity_obj, *args, **kwargs)

    return f_wrapper

  return get_entity_decorator


def get_entity_of_resource(f):

  def f_wrapper(*args, **kwargs):
    entity_obj = args[0].entity.query.filter_by(
        public_id=kwargs[args[0].entity_name + "_id"]).first()
    if entity_obj is None:
      return {"message": "No entity found"}, 404

    return f(entity_obj=entity_obj, *args, **kwargs)

  return f_wrapper
