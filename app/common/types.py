from typing import Union

from app.models.consolidated_city import ConsolidatedCity
from app.models.county import County
from app.models.place import Place
from app.models.state import State

LocationObjType = Union[State, County, Place, ConsolidatedCity]
