from app.models.scholarship import Scholarship

#TODO: add failure tests
def test_scholarships(client, college_id):
    college_scholarships_url = "/api/colleges/" + college_id + "/scholarships"
    scholarships_url = "/api/scholarships"

    response = client.post(college_scholarships_url, json={"name": "test scholarship"})
    response_json = response.get_json()

    assert response.status_code == 200
    assert "scholarship_id" in response_json

    scholarship_id = response_json["scholarship_id"]

    response = client.get(scholarships_url)
    response_json = response.get_json()

    assert response.status_code == 200
    assert "items" in response_json
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["public_id"] == scholarship_id


    response = client.put(scholarships_url + '/' + scholarship_id, json={"sat": 100, "act": 32})
    response_json = response.get_json()

    assert response.status_code == 200
    assert "scholarship" in response_json
    assert response_json["scholarship"]["public_id"] == scholarship_id

    response = client.get(scholarships_url + '/' + scholarship_id)
    response_json = response.get_json()

    assert response.status_code == 200
    assert "scholarship" in response_json
    assert response_json["scholarship"]["sat"] == 100
    assert response_json["scholarship"]["act"] == 32

    response = client.delete(scholarships_url + '/' + scholarship_id)
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["message"] == "scholarship deleted"

    response = client.get(scholarships_url + '/' + scholarship_id)
    response_json = response.get_json()

    assert response.status_code == 404
    assert response_json["message"] == "scholarship not found"

def test_scholarship_programs(client, scholarship_id):
  def check_programs(program_1: dict, program_2: dict):
    assert "name" in program_1 and "name" in program_2

    for k in program_1.keys():
      if k in program_2:
        assert program_1[k] == program_2[k]

  url = "api/scholarships/" + scholarship_id + "/programs"
  response = client.get(url)
  response_json = response.get_json()

  assert response.status_code == 200
  assert len(response_json["programs"]) == 0

  programs = {"programs": [
    {"name": "program 1"},
    {"name": "program 2"},
    {"name": "program 3", "round_qualification": "finalist"},
  ]}
  response = client.post(url, json=programs)
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json["message"] == "programs added"

  response = client.get(url)
  response_json = response.get_json()

  assert "programs" in response_json and len(response_json["programs"]) == 3

  for i, program in enumerate(response_json["programs"]):
    check_programs(program, programs["programs"][i])

  response = client.delete(url, json={"programs": [programs["programs"][1]["name"]]})
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json["message"] == "programs removed"

  response = client.get(url)
  response_json = response.get_json()

  assert "programs" in response_json and len(response_json["programs"]) == 2

  check_programs(programs["programs"][0], response_json["programs"][0])
  check_programs(programs["programs"][2], response_json["programs"][1])
  
def test_scholarship_ethnicities(client, scholarship_id):
  def check_ethnicities(ethnicity_1: dict, ethnicity_2: dict):
    assert "name" in ethnicity_1 and "name" in ethnicity_2

    for k in ethnicity_1.keys():
      if k in ethnicity_2:
        assert ethnicity_1[k] == ethnicity_2[k]

  url = "api/scholarships/" + scholarship_id + "/ethnicities"
  response = client.get(url)
  response_json = response.get_json()

  assert response.status_code == 200
  assert len(response_json["ethnicities"]) == 0

  ethnicities = {"ethnicities": [
    {"name": "ethnicity 1"},
    {"name": "ethnicity 2"},
    {"name": "ethnicity 3"},
  ]}
  response = client.post(url, json=ethnicities)
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json["message"] == "ethnicities added"

  response = client.get(url)
  response_json = response.get_json()

  assert "ethnicities" in response_json and len(response_json["ethnicities"]) == 3

  for i, ethnicity in enumerate(response_json["ethnicities"]):
    check_ethnicities(ethnicity, ethnicities["ethnicities"][i])

  response = client.delete(url, json={"ethnicities": [ethnicities["ethnicities"][1]["name"]]})
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json["message"] == "ethnicities removed"

  response = client.get(url)
  response_json = response.get_json()

  assert "ethnicities" in response_json and len(response_json["ethnicities"]) == 2

  check_ethnicities(ethnicities["ethnicities"][0], response_json["ethnicities"][0])
  check_ethnicities(ethnicities["ethnicities"][2], response_json["ethnicities"][1])

def test_scholarships_needed(client, scholarship_id, college_id):
  url = "api/scholarships/" + scholarship_id + "/scholarships_needed"
  create_scholarship_url = "api/colleges/" + college_id + "/scholarships"
  response = client.post(create_scholarship_url, json={"name": "scholarship test _1"})
  response_json = response.get_json()

  assert response.status_code == 200

  scholarship_test_1 = response_json["scholarship_id"]

  response = client.post(create_scholarship_url, json={"name": "scholarship test _2"})
  response_json = response.get_json()

  assert response.status_code == 200

  scholarship_test_2 = response_json["scholarship_id"]

  response = client.post("api/colleges/" + college_id + "/scholarships/" + scholarship_id + "/scholarships_needed",
                         json={"scholarships_needed": [scholarship_test_1, scholarship_test_2]})
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json["message"] == "needed scholarships added"

  response = client.get(url)
  response_json = response.get_json()

  assert response.status_code == 200
  assert len(response_json["scholarships_needed"]) == 2

  assert response_json["scholarships_needed"][0]["public_id"] == scholarship_test_1
  assert response_json["scholarships_needed"][1]["public_id"] == scholarship_test_2

  response = client.delete(url, json={"scholarships_needed": [scholarship_test_2]})
  response_json = response.get_json()

  assert response.status_code == 200
  assert response_json["message"] == "needed scholarships removed"

  response = client.get(url)
  response_json = response.get_json()

  assert response.status_code == 200
  assert len(response_json["scholarships_needed"]) == 1

  assert response_json["scholarships_needed"][0]["public_id"] == scholarship_test_1
