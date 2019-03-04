from decimal import Decimal
import flask

from app import db
from app.models.major import Major

url = "/api/majors"


def test_get_majors(app, client, auth):
    """ get all majors and test search function """

    # create majors to test

    majors_properties = []

    with app.app_context():
        for i in range(50):

            majors_properties.append({"name": f"test major {i}"})

            major = Major(**majors_properties[i])
            db.session.add(major)

        db.session.commit()

    # login

    auth.login()

    # get majors

    response = client.get(url)
    data = response.get_json()
    majors = data["items"]

    for i, major in enumerate(majors):
        assert major["name"] == majors_properties[i]["name"]

    # get major that ends with "or 2"

    response = client.get(url + "?search=or 2")
    data = response.get_json()
    majors = data["items"]

    for major in majors:
        assert major["name"].find("or 2") != -1