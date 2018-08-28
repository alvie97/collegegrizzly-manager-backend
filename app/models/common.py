from flask import url_for
from app import db
from datetime import datetime


class PaginatedAPIMixin(object):

  @staticmethod
  def to_collection_dict(query, page=0, per_page=0, endpoint='', **kwargs):
    resources = query.paginate(page, per_page, False)
    data = {
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

    return data


class DateAudit(object):

  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(
      db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  def audit_dates(self):
    return {
        "created_at": self.created_at.isoformat() + 'Z',
        "updated_at": self.updated_at.isoformat() + 'Z'
    }


class BaseMixin(object):

  def from_dict(self, data):
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])
