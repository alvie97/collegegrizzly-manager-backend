from app.models.consolidated_city import ConsolidatedCity
from app.models.county import County
from app.models.place import Place
from app.models.state import State

from flask_sqlalchemy.model import Model
from sqlalchemy.orm.query import Query
from typing import Union

LocationObjType = Union[State, County, Place, ConsolidatedCity]
SqlalchemyQuery = Query
SqlalchemyModel = Model
