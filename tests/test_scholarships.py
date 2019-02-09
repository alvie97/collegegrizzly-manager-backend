from app.common.utils import generate_public_id
from app import db
from app.models.scholarship import Scholarship
from decimal import Decimal
from app.cli import _save_states

url = "/api/scholarships"

def test_get_scholarships(app, client, auth):
    """ get all scholarships and test search function """

    # add scholarships to database
    scholarships_properties = []

    with app.app_context():
        for i in range(50):

            scholarships_properties.append({"name": f"test scholarship {i}"})

            scholarship = Scholarship(**scholarships_properties[i])
            db.session.add(scholarship)

        db.session.commit()

    # login

    auth.login()

    # get scholarships

    response = client.get(url)
    data = response.get_json()
    scholarships = data["items"]

    for i, scholarship in enumerate(scholarships):
        assert scholarship["name"] == scholarships_properties[i]["name"]

    # get scholarship that ends with "ge 2"

    response = client.get(url + "?search=ship 2")
    data = response.get_json()
    scholarships = data["items"]

    for scholarship in scholarships:
        assert scholarship["name"].find("ship 2") != -1
