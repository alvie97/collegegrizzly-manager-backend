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
