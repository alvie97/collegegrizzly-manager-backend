import os

import flask
import marshmallow

import app
from app import pictures as pictures_module
from app import security, utils
from app.models import college as college_model
from app.models import picture as picture_model


@pictures_module.bp.route("/<string:public_id>")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(picture_model.Picture, "public_id")
def get_picture(picture):
    """Gets picture.

    Retrieves single picture from database.

    GET:
        Params:
            public_id (string) (required): public id of picture.
    
    Responses:
        200:
            Successfully retieves picture. Returns picture.

            produces:
                Application/json.
        
        404:
            College not found, returns message.

            produces:
                Application/json.
    """
    return flask.jsonify(picture.to_dict())


@pictures_module.bp.route("/<string:public_id>", methods=["PATCH"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(picture_model.Picture, "public_id")
def patch_picture(picture):
    """Edits picture.

    Modifies picture model.

    PATCH:
        Params:
            public_id (string) (required): public id of picture.

        Consumes:
            Application/json.
        
        Request Body:
            Dictionary of editable picture fields.
        
        Example::
            {
                "type": "example picture name"
            }
    
    Responses:
        200:
            Picture successfully modified. Returns message.

            Produces:
                Application/json.
        
        400:
            Empty json object. Returns message "no data provided".

            produces:
                Application/json.
        404:
            Picture not found, returns message.

            produces:
                Application/json.
        422:
            some or all of the fields are invalid. Returns error of 
            invalid fields.

            produces:
                Application/json.
    """
    data = flask.request.get_json()

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    #TODO: create photo schema to validate fields like type, where it should
    #       only take the values logo and campus.
    if "type" in data and data["type"] == "logo":
        college_logo = picture.college.pictures.filter_by(type="logo").first()

        if college_logo is not None:
            college_logo.update({"type": "campus"})

    picture.update({"type": data["type"]})
    app.db.session.commit()
    return flask.jsonify(data)


@pictures_module.bp.route("/<string:public_id>", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
@utils.get_entity(picture_model.Picture, "public_id")
def delete_picture(picture):
    """Deletes picture.

    Deletes picture from database.

    DELETE:
        Params:
            public_id (string) (required): public id of picture.
    
    Responses:
        200:
            Picture successfully deleted from database. Return message.

            Produces:
                Application/json.
        404:
            Picture not found, returns message.

            produces:
                Application/json.
    """
    app.db.session.delete(picture)
    app.db.session.commit()
    return flask.jsonify({"message": "picture deleted"})


@pictures_module.bp.route("")
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def get_pictures():
    """Gets pictures in database

    Retrieves paginated list of all pictures from database.

    GET:
        Request params:
            page (int) (optional): Page number in paginated resource, defaults 
            to one.
            per_page (int) (optional): Number of items to retrieve per page, 
            defaults to configuration constant PER_PAGE.
            search (string) (optional): Search query keyword, defaults to "".
    
    Responses:
        200:
            Successfully retrieves items from database. Returns paginated list
            of pictures.

            produces:
                Application/json.

            Example::
                return {
                    "items": [list of pictures],
                    "_meta": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 15,
                        "total_items": 72 
                    },
                    "_links": {
                        "self": {
                            "url": self_url,
                            "params": request parameters,
                        },
                        "next": next page"s url or None if there"s no page,
                        "prev": previous page"s url or None if there"s no page,
                    }
                }
    """
    page = flask.request.args.get("page", 1, type=int)
    per_page = flask.request.args.get(
        "per_page", flask.current_app.config["PER_PAGE"], type=int)

    data = picture_model.Picture.to_collection_dict(
        picture_model.Picture.query, page, per_page, "pictures.get_pictures")

    return flask.jsonify(data)


@pictures_module.bp.route("", methods=["DELETE"])
@security.user_role([security.ADMINISTRATOR, security.BASIC])
def delete_pictures():
    """Deletes pictures.

    Deletes pictures from database.

    DELETE:
        Consumes:
            Application/json.
        
        Request Body:
            list of pictures public ids.
    
    Responses:
        200:
            Pictures successfully deleted from database. Returns message.

            Produces:
                Application/json.
        400:
            No picture ids given, returns message.

            produces:
                Application/json.
    """
    data = flask.request.get_json() or {}

    if not data:
        return flask.jsonify({"message": "no data provided"}), 400

    pictures = picture_model.Picture.query.filter(
        picture_model.Picture.public_id.in_(data)).all()

    for picture in pictures:
        picture.delete()
    app.db.session.commit()

    return flask.jsonify({"message": "pictures deleted"})
