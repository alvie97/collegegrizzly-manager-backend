from typing import Any, Optional
from urllib import parse

from flask import url_for
from flask_sqlalchemy.model import Model as SqlalchemyModel


class PaginatedAPIMixin(object):

    @staticmethod
    def to_collection_dict(query, page=0, per_page=0, endpoint="", **kwargs):
        """Returns a dictionary of a paginated collection of model instances."""
        resources = query.paginate(page, per_page, False)

        self_url = url_for(endpoint, page=page, per_page=per_page, **kwargs)
        return {
            "items": [item.for_pagination() for item in resources.items],
            "meta": {
                "page": page,
                "per_page": per_page,
                "total_pages": resources.pages,
                "total_items": resources.total
            },
            "links": {
                "self": {
                    "url": self_url,
                    "params": dict(
                        parse.parse_qsl(parse.urlsplit(self_url).query))
                },
                "next":
                url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                if resources.has_next else None,
                "prev":
                url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                if resources.has_prev else None
            }
        }
