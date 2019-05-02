import app as application
from app.models import college as college_model
from app.models import location as location_model

url = "api/colleges/1/location_requirements/"


def test_delete_lr_to_college_sucess_0(app, client, auth, colleges):
    """
    Deletes location requirement from college
    """
    auth.login()
    with app.app_context():
        college = college_model.College.query.first()
        location = location_model.Location(zip_code="12345")

        application.db.session.add(location)

        college.add_location_requirement(location)

        application.db.session.commit()

        location_id = location.id

    response = client.delete(url + str(location_id))

    assert response.status_code == 200
    assert response.get_json(
    )["message"] == "location requirement removed from college"

    with app.app_context():
        college = college_model.College.query.first()

        assert college.location_requirements.count() == 0


def test_delete_lr_to_college_failure_0(app, client, auth, colleges):
    """
    test delete location requirement from college failure case.
    """
    auth.login()
    with app.app_context():
        college = college_model.College.query.first()
        location = location_model.Location(zip_code="12345")

        application.db.session.add(location)

        college.add_location_requirement(location)

        application.db.session.commit()

    response = client.delete(url + '2')

    assert response.status_code == 404
    assert response.get_json(
    )["message"] == "college doesn't have location requirement"
