import app as application
from app.models import college as college_model
from app.models import location as location_model

url = "api/colleges/1/location_requirements"


def test_get_college_location_requirements(app, client, auth, colleges):
    """
    Test get college location requirements
    """
    json = []

    with app.app_context():
        college = college_model.College.query.first()
        location = location_model.Location(zip_code="12345")

        json.append(location.to_dict())
        location = location_model.Location(zip_code="12346", blacklist=True)

        application.db.session.add(location)

        college.add_location_requirement(location)

        application.db.session.commit()

    response = client.get(url)

    assert response.status_code == 200
    assert response.get_json() == json