from app import db
from app.common.utils import generate_public_id
from app.models.college import College


def test_get_colleges(client):
  assert client.get("/api/colleges").status_code == 200


def test_post_college(client):
  request_result = client.post("/api/colleges", json={"name": "college test"})
  assert request_result.status_code == 200
  assert "college_id" in request_result.get_json()


def test_update_college(app, client):

  with app.app_context():
    college_test = College.query.first()

    if college_test is None:
      college_test = College(
          public_id=generate_public_id(), name="college test")

      db.session.add(college_test)
      db.session.commit()

    public_id = college_test.public_id

  request_result = client.put(
      "/api/colleges/" + public_id, json={"location": "testing location"})

  assert request_result.status_code == 200

  with app.app_context():
    college_test = College.first(public_id=public_id)

    assert college_test is not None
    assert college_test.location == "testing location"


def test_delete_college(app, client):

  with app.app_context():
    college_test = College.query.first()

    if college_test is None:
      college_test = College(
          public_id=generate_public_id(), name="college test")

      db.session.add(college_test)
      db.session.commit()

    public_id = college_test.public_id

  request_result = client.delete("/api/colleges/" + public_id)

  assert request_result.status_code == 200

  with app.app_context():
    college_test = College.first(public_id=public_id)

    assert college_test is None


def test_college_majors(college_id, app, client):

  # 1. add major(s)
  # 2. get majors(s)
  # 3. delete major(s)

  def check_majors(major_1, major_2):
    assert "name" in major_1 and "name" in major_2

    for k in major_1.keys():
      if k in major_2:
        assert major_1[k] == major_2[k]

  url = "/api/colleges/" + college_id + "/majors"

  majors_test = [{
      "name": "major test 1"
  }, {
      "name": "major test 2",
      "description": "major test 2 description"
  }, {
      "name": "major test 3"
  }]

  request = client.post(url, json={"majors": majors_test})

  assert request.status_code == 200
  assert request.get_json()["message"] == "majors added"

  request = client.get(url)

  assert request.status_code == 200
  majors_added = request.get_json()
  assert "majors" in majors_added

  for i, major in enumerate(majors_test):
    check_majors(major, majors_added["majors"][i])

  request = client.delete(
      url, json={"majors": [majors_test[0]["name"], majors_test[2]["name"]]})

  assert request.status_code == 200
  assert request.get_json()["message"] == "majors removed"

  request = client.get(url)

  assert request.status_code == 200
  majors_removed = request.get_json()

  check_majors(majors_test[1], majors_removed["majors"][0])
