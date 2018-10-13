def test_college(client):
  url = "/api/colleges"
  response = client.post(url, json={"name": "college test"})
  response_json = response.get_json()

  assert response.status_code == 200
  assert "college_id" in response.get_json()

  college_id = response_json["college_id"]

  response = client.patch(
      url + '/' + college_id, json={"location": "testing location"})
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json == "college saved successfully"

  response = client.get(url + '/' + college_id)
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json["college"]["editable_fields"][
      "location"] == "testing location"

  response = client.get(url)
  response_json = response.get_json()

  assert response.status_code == 200
  assert len(response_json["items"]) > 0
  assert response_json["items"][0]["public_id"] == college_id

  response = client.delete(url + '/' + college_id)
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json["message"] == "college deleted"

  response = client.get(url + '/' + college_id)
  response_json = response.get_json()

  assert response.status_code == 404
  assert response_json["message"] == "college not found"


def test_college_majors(college_id, client):
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
