import functools
import uuid
import flask
import app
from app import errors


def generate_public_id():
    """Generates public id
    
    Returns:
        string: uuid without dashes.
    """
    return str(uuid.uuid4()).replace('-', '')


def get_entity(entity, search_key="id", uri_param_name="id"):
    """Adds entity as argument to wrapped function.

    Args:
        entity (sqlalchemy.Model): database model.
        search_key (string): database model property name.
        uri_param_name (string) (optional): route param unique name.

    Returns:
        Obj (Flask response): if entity not found, returns message and 404 code.
    """

    def get_entity_decorator(f):

        @functools.wraps(f)
        def f_wrapper(*args, **kwargs):
            search_arguments = {search_key: kwargs[uri_param_name]}
            entity_obj = entity.first(**search_arguments)
            entity_name = to_snake_case(entity.__tablename__)

            if entity_obj is None:
                return flask.jsonify({
                    "message": entity_name + " not found"
                }), 404

            kwargs[entity_name] = entity_obj
            del kwargs[uri_param_name]

            return f(*args, **kwargs)

        return f_wrapper

    return get_entity_decorator


def to_snake_case(word):
    """Snake cases string.

    Args:
        word (string): string to snake case.
    Returns:
        string: snake cased string.
    """

    result = ""
    for i, character in enumerate(word):
        if i > 0 and character.isupper():
            if word[i - 1].islower() or (i + 1 < len(word) and
                                         word[i + 1].islower()):
                result = result + "_"

        result = result + character.lower()

    return result