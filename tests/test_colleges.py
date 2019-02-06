from app.common.utils import generate_public_id
from app import db
from app.models.college import College


def test_get_colleges(app, client, auth):
    """ get all colleges and test search function """

    url = "/api/colleges"

    # create colleges to test

    colleges_properties = []

    with app.app_context():
        for i in range(50):

            colleges_properties.append({
                "name": f"test college {i}",
                "public_id": generate_public_id()
            })

            college = College(**colleges_properties[i])
            db.session.add(college)

        db.session.commit()

    # login

    login_response = auth.login()

    # get colleges

    response = client.get(url)
    data = response.get_json()
    colleges = data["items"]

    for i, college in enumerate(colleges):
        assert college["name"] == colleges_properties[i]["name"] and college[
            "public_id"] == colleges_properties[i]["public_id"]

    # get college that ends with "ge 2"

    response = client.get(url + "?search=ge 2")
    data = response.get_json()
    colleges = data["items"]

    for college in colleges:
        assert college["name"].find("ge 2") != -1