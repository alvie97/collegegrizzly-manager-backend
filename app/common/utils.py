from app.models.common.base_mixin import BaseMixin
from uuid import uuid4
from typing import Callable, Union, Any, Tuple, Dict
from flask_sqlalchemy.model import Model
from functools import wraps


def generate_public_id() -> str:
  return str(uuid4()).replace('-', '')


def get_entity(entity: BaseMixin, entity_name: str) -> Model:

  def get_entity_decorator(f: Callable) -> Callable:

    @wraps(f)
    def f_wrapper(*args, **kwargs) -> Union[Any, Tuple[Dict[str, str], int]]:
      entity_obj = entity.first(public_id=kwargs[entity_name + "_id"])

      if entity_obj is None:
        return {"message": entity_name + " not found"}, 404

      kwargs[entity_name] = entity_obj
      del kwargs[entity_name + "_id"]
      return f(*args, **kwargs)

    return f_wrapper

  return get_entity_decorator


# TODO: change entity_obj param like the get_entity function
def get_entity_of_resource(f: Callable) -> Callable:

  def f_wrapper(*args, **kwargs) -> Union[Any, Tuple[Dict[str, str], int]]:
    entity_obj = args[0].entity.first(public_id=kwargs[args[0].entity_name +
                                                       "_id"])
    if entity_obj is None:
      return {"message": "entity not found"}, 404

    return f(entity_obj=entity_obj, *args, **kwargs)

  return f_wrapper
