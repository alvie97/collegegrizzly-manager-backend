from flask              import current_app, url_for
from app                import db

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page=0, per_page=0, endpoint='', paginate=True, **kwargs):
        data = {}
        if paginate:
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
                    'self': url_for(endpoint, page=page, per_page=per_page,
                                    **kwargs),
                    'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                    **kwargs) if resources.has_next else None,
                    'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                    **kwargs) if resources.has_prev else None
                }
            }
        else:
            resources = query.all()
            data = {
                'items': [item.to_dict() for item in resources],
            }

        return data
