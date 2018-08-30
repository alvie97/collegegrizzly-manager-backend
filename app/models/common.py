


class PaginatedAPIMixin(object):

  @staticmethod
  def to_collection_dict(query: SqlalchemyModel,
                         page: Optional[int] = 0,
                         per_page: Optional[int] = 0,
                         endpoint: Optional[str] = '',
                         **kwargs: Any) -> dict:
    """
    Returns a dictionary of a paginated collection of model instances
    """
    resources = query.paginate(page, per_page, False)
    return {
        'items': [item.to_dict() for item in resources.items],
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': resources.pages,
            'total_items': resources.total
        },
        '_links': {
            'self':
                url_for(endpoint, page=page, per_page=per_page, **kwargs),
            'next':
                url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                if resources.has_next else None,
            'prev':
                url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                if resources.has_prev else None
        }
    }


class DateAudit(object):

  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(
      db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  def audit_dates(self) -> dict:
    """
    Returns date properties for audit
    """
    return {
        "created_at": self.created_at.isoformat() + 'Z',
        "updated_at": self.updated_at.isoformat() + 'Z'
    }


class LocationMixin(object):

  @declared_attr
  def location_requirement_states(cls):
    class_name = cls.__name__.to_lower()
    return db.relationship(
        "State",
        secondary=class_name + "_state",
        backref=db.backref(class_name + "_list", lazy="dynamic"),
        lazy="dynamic")

  @declared_attr
  def location_requirement_counties(cls):
    class_name = cls.__name__.to_lower()
    return db.relationship(
        "County",
        secondary=class_name + "_county",
        backref=db.backref(class_name + "_list", lazy="dynamic"),
        lazy="dynamic")

  @declared_attr
  def location_requirement_places(cls):
    class_name = cls.__name__.to_lower()
    return db.relationship(
        "Place",
        secondary=class_name + "_place",
        backref=db.backref(class_name + "_list", lazy="dynamic"),
        lazy="dynamic")

  @declared_attr
  def location_requirement_consolidated_cities(cls):
    class_name = cls.__name__.to_lower()
    return db.relationship(
        "ConsolidatedCity",
        secondary=class_name + "_consolidated_city",
        backref=db.backref(class_name + "_list", lazy="dynamic"),
        lazy="dynamic")

  def get_location_entity_query(self, location_obj: LocationObjType
                               ) -> Tuple[LocationObjType, SqlalchemyQuery]:
    """
    Returns a tuple of the location entity (Model) and the location requirement
    query object corresponding to that entity in the Model that inherits the
    LocationMixin
    """
    if isinstance(location_obj, State):
      location_query = self.location_requirement_states
      location_entity = State
    elif isinstance(location_obj, County):
      location_query = self.location_requirement_counties
      location_entity = County
    elif isinstance(location_obj, Place):
      location_query = self.location_requirement_places
      location_entity = Place
    elif isinstance(location_obj, ConsolidatedCity):
      location_query = self.location_requirement_consolidated_cities
      location_entity = ConsolidatedCity
    else:
      raise LocationEntityError(
          "location object is not an instance of a location")

    return location_entity, location_query

  def add_location(self, location_obj: LocationObjType):
    """
    Adds location obj to Model relationship
    """
    try:
      instance = self.get_location_entity_query(location_obj)
    except LocationEntityError as err:
      raise

    location_entity, location_query = instance

    try:
      if not self.has_location(location_entity, location_obj.fips_code):
        location_query.append(location_obj)
    except LocationEntityError as err:
      raise

  def remove_location(self, location_obj: LocationObjType):
    """
    Removes location obj from Model relationship
    """
    try:
      instance = self.get_location_entity_query(location_obj)
    except LocationEntityError as err:
      raise

    location_entity, location_query = instance

    try:
      if self.has_location(location_entity, location_obj.fips_code):
        location_query.remove(location_obj)
    except LocationEntityError as err:
      raise

  def has_location(self, location_entity: LocationObjType,
                   fips_code: str) -> bool:
    """
    Checks if model has a location with the corresponding fips
    """
    if location_entity is State:
      location_query = self.location_requirement_states
    elif location_entity is County:
      location_query = self.location_requirement_counties
    elif location_entity is Place:
      location_query = self.location_requirement_places
    elif location_entity is ConsolidatedCity:
      location_query = self.location_requirement_consolidated_cities
    else:
      raise LocationEntityError("location entity is not a location model")

    return location_query.filter(
        location_entity.fips_code == fips_code).count() > 0

  def get_location_requirement(self, location_entity: LocationObjType,
                               base_endpoint: str, page: int, per_page: int,
                               **endpoint_args) -> dict:
    """Returns paginated list of locations as a dictionary"""

    if location_entity is State:
      location_name = "states"
      location_query = self.location_requirement_states
      location_url = base_endpoint + "_states"
    elif location_entity is County:
      location_name = "counties"
      location_query = self.location_requirement_counties
      location_url = base_endpoint + "_counties"
    elif location_entity is Place:
      location_name = "places"
      location_query = self.location_requirement_places
      location_url = base_endpoint + "_places"
    elif location_entity is ConsolidatedCity:
      location_name = "consolidated_cities"
      location_query = self.location_requirement_consolidated_cities
      location_url = base_endpoint + "_cities"
    else:
      raise LocationEntityError("location entity is not a location model")

    return {
        location_name:
            self.to_collection_dict(location_query, page, per_page,
                                    location_url, **endpoint_args)
    }

  def location_requirement_endpoints(self, base_endpoint: str,
                                     **endpoint_args) -> dict:
    """Returns all enpoints to get all location requirements"""
    return {
        "states":
            url_for(base_endpoint + "_states", **endpoint_args),
        "counties":
            url_for(base_endpoint + "_counties", **endpoint_args),
        "places":
            url_for(base_endpoint + "_places", **endpoint_args),
        "consolidated_cities":
            url_for(base_endpoint + "_consolidated_cities", **endpoint_args)
    }


class BaseMixin(object):

  def get(self, id):
    """ Returns an instance of model by id :param id: model id """

    return self.query.get(id)

  def get_all(self, ids=None):
    """
    Returns list of all model instances, if id list is specified, all instances
    in that list are returned
    """

    return self.query.all() if not ids else self.query.filter(
        self.id.in_(ids)).all()

  def find(self, **kwargs):
    """
    Returns list of all model instances filtered by specified keys
    """

    return self.query.filter_by(**kwargs)

  def first(self, **kwargs):
    """
    Returns first model instance that meets parameters
    """

    return self.query.filter_by(**kwargs).first()

  def update(self, data):
    """
    updates updatable fields in ATTR_FIELDS with the data provided
    """
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
