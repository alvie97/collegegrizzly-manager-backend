import app as application
from app.models import scholarship as scholarship_model
from app.models import location as location_model

url = "api/scholarships/1/location_requirements/"


def test_delete_lr_to_scholarship_sucess_0(app, client, auth, scholarships):
    """
    Deletes location requirement from scholarship
    """
    auth.login()
    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        location = location_model.Location(zip_code="12345")

        application.db.session.add(location)

        scholarship.add_location_requirement(location)

        application.db.session.commit()

        location_id = location.id

    response = client.delete(url + str(location_id))

    assert response.status_code == 200
    assert response.get_json(
    )["message"] == "location requirement removed from scholarship"

    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()

        assert scholarship.location_requirements.count() == 0


def test_delete_lr_to_scholarship_failure_0(app, client, auth, scholarships):
    """
    test delete location requirement from scholarship failure case.
    """
    auth.login()
    with app.app_context():
        scholarship = scholarship_model.Scholarship.query.first()
        location = location_model.Location(zip_code="12345")

        application.db.session.add(location)

        scholarship.add_location_requirement(location)

        application.db.session.commit()

    response = client.delete(url + '2')

    assert response.status_code == 404
    assert response.get_json(
    )["message"] == "scholarship doesn't have location requirement"
