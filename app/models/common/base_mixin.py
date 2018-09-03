class BaseMixin(object):

  @classmethod
  def get(cls, id):
    """ Returns an instance of model by id :param id: model id """

    return cls.query.get(id)

  @classmethod
  def get_all(cls, ids=None):
    """
    Returns list of all model instances, if id list is specified, all instances
    in that list are returned
    """

    return cls.query.all() if not ids else cls.query.filter(
        cls.id.in_(ids)).all()

  @classmethod
  def find(cls, **kwargs):
    """
    Returns list of all model instances filtered by specified keys
    """

    return cls.query.filter_by(**kwargs)

  @classmethod
  def first(cls, **kwargs):
    """
    Returns first model instance that meets parameters
    """

    return cls.query.filter_by(**kwargs).first()

  def update(self, data):
    """
    updates updatable fields in ATTR_FIELDS with the data provided
    """
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
