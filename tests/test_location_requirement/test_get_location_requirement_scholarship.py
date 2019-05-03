import app as application
from app.models import scholarship as scholarship_model
from app.models import location as location_model

url = "api/scholarships/1/location_requirements"


def test_get_scholarship_location_requirements(app, client, auth,
                                               scholarships):
    """
    Test get scholarship location requirements
    """
    json = []

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        location_0 = location_model.Location(zip_code="12345")

        location_1 = location_model.Location(zip_code="12346", blacklist=True)

        application.db.session.add(location_0)
        application.db.session.add(location_1)

        scholarship.add_location_requirement(location_0)
        scholarship.add_location_requirement(location_1)

        application.db.session.commit()

        json = {
            "accepted": [location_0.to_dict()],
            "blacklisted": [location_1.to_dict()]
        }

    auth.login()
    response = client.get(url)

    assert response.status_code == 200
    assert response.get_json() == json


def test_get_scholarship_location_requirements_failure(app, client, auth,
                                                       scholarships):
    """
    Test get scholarship location requirements failure case.
    """
    auth.login()
    response = client.get("api/3000/scholarships/location_requirements")

    assert response.status_code == 404