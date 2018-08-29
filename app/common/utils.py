from uuid import uuid4
from typing import Union, Tuple, Dict, Callable, Any
from app.models.state import State
from app.models.county import County
from app.models.place import Place
from app.models.consolidated_city import ConsolidatedCity
from sqlalchemy.orm.query import Query
from flask_sqlalchemy.model import Model
from app.models.common import BaseMixin
from app.main.resources.common.utils import LocationRequirement

LocationObjType = Union[State, County, Place, ConsolidatedCity]
SqlalchemyQuery = Query
SqlalchemyModel = Model


def generate_public_id() -> str:
  return str(uuid4()).replace('-', '')


def get_entity(entity: BaseMixin, entity_name: str) -> Model:

  def get_entity_decorator(f: Callable) -> Callable:

    def f_wrapper(*args, **kwargs) -> Union[Any, Tuple[Dict[str], int]]:
      entity_obj = entity.first(public_id=kwargs[entity_name + "_id"])

      if entity_obj is None:
        return {"message": "No " + entity_name + " found"}, 404

      kwargs[entity_name] = entity_obj
      del kwargs[entity_name + "_id"]
      return f(*args, **kwargs)

    return f_wrapper

  return get_entity_decorator


# TODO: change entity_obj param like the get_entity function
def get_entity_of_resource(f: Callable) -> Callable:

  def f_wrapper(*args: LocationRequirement,
                **kwargs: str) -> Union[Any, Tuple[Dict[str], int]]:
    entity_obj = args[0].entity.first(public_id=kwargs[args[0].entity_name +
                                                       "_id"])
    if entity_obj is None:
      return {"message": "No entity found"}, 404

    return f(entity_obj=entity_obj, *args, **kwargs)

  return f_wrapper
