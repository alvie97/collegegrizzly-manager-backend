from app.models.college import College
from app.models.consolidated_city import ConsolidatedCity
from app.models.county import County
from app.models.place import Place
from app.models.scholarship import Scholarship
from app.models.state import State
from app.cli import _save_states


def test_location_requirements(app, client, scholarship_id):
  with app.app_context():
    _save_states(2)
    scholarship = Scholarship.first(public_id=scholarship_id)
    college_id = scholarship.college.public_id

  response = client.get("/api/locations/states/search/alabama")

  assert response.status_code == 200
  alabama = response.get_json()["state"]
  assert alabama["name"] == "Alabama"
  assert "fips_code" in alabama

  response = client.get("/api/locations/states/02")
  alaska = response.get_json()["state"]

  assert alaska["name"] == "Alaska"

  response = client.post(
      f"/api/colleges/{college_id}/states",
      json={"location_fips": [alabama["fips_code"], alaska["fips_code"]]})

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  response = client.get(f"/api/colleges/{college_id}/states")

  assert response.status_code == 200
  states = response.get_json()["states"]["items"]

  assert [states[0]["fips_code"], states[1]["fips_code"]] == [
      alabama["fips_code"], alaska["fips_code"]
  ]

  response = client.post(
      f"/api/scholarships/{scholarship_id}/states",
      json={"location_fips": [alabama["fips_code"], alaska["fips_code"]]})

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  response = client.get(f"/api/scholarships/{scholarship_id}/states")

  assert response.status_code == 200
  states = response.get_json()["states"]["items"]

  assert [states[0]["fips_code"], states[1]["fips_code"]] == [
      alabama["fips_code"], alaska["fips_code"]
  ]


def test_counties_requirement(app, client, scholarship_id):
  with app.app_context():
    _save_states(1)
    scholarship = Scholarship.first(public_id=scholarship_id)
    college_id = scholarship.college.public_id

  response = client.get("/api/locations/states/search/alabama")

  assert response.status_code == 200
  alabama = response.get_json()["state"]
  assert alabama["name"] == "Alabama"
  assert "fips_code" in alabama

  response = client.get(alabama["_links"]["counties"])
  assert response.status_code == 200

  counties = response.get_json()["counties"]["items"]

  response = client.post(
      f"/api/colleges/{college_id}/counties",
      json={
          "location_fips": [
              counties[0]["fips_code"], counties[1]["fips_code"]
          ]
      })

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  response = client.get(f"/api/colleges/{college_id}/counties")

  assert response.status_code == 200
  counties_response = response.get_json()["counties"]["items"]

  assert [
      counties_response[0]["fips_code"], counties_response[1]["fips_code"]
  ] == [counties[0]["fips_code"], counties[1]["fips_code"]]

  response = client.post(
      f"/api/scholarships/{scholarship_id}/counties",
      json={
          "location_fips": [
              counties[0]["fips_code"], counties[1]["fips_code"]
          ]
      })

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  response = client.get(f"/api/scholarships/{scholarship_id}/counties")

  assert response.status_code == 200
  counties_response = response.get_json()["counties"]["items"]

  assert [
      counties_response[0]["fips_code"], counties_response[1]["fips_code"]
  ] == [counties[0]["fips_code"], counties[1]["fips_code"]]


def test_location_places(app, client, scholarship_id):
  with app.app_context():
    _save_states(1)
    scholarship = Scholarship.first(public_id=scholarship_id)
    college_id = scholarship.college.public_id

  response = client.get("/api/locations/states/search/alabama")

  assert response.status_code == 200
  alabama = response.get_json()["state"]
  assert alabama["name"] == "Alabama"
  assert "fips_code" in alabama

  response = client.get(alabama["_links"]["places"])
  assert response.status_code == 200

  places = response.get_json()["places"]["items"]

  response = client.post(
      f"/api/colleges/{college_id}/places",
      json={"location_fips": [places[0]["fips_code"], places[1]["fips_code"]]})

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  response = client.get(f"/api/colleges/{college_id}/places")

  assert response.status_code == 200
  places_response = response.get_json()["places"]["items"]

  assert [places_response[0]["fips_code"], places_response[1]["fips_code"]
         ] == [places[0]["fips_code"], places[1]["fips_code"]]

  response = client.post(
      f"/api/scholarships/{scholarship_id}/places",
      json={"location_fips": [places[0]["fips_code"], places[1]["fips_code"]]})

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  response = client.get(f"/api/scholarships/{scholarship_id}/places")

  assert response.status_code == 200
  places_response = response.get_json()["places"]["items"]

  assert [places_response[0]["fips_code"], places_response[1]["fips_code"]
         ] == [places[0]["fips_code"], places[1]["fips_code"]]


def test_location_consolidated_cities(app, client, scholarship_id):
  with app.app_context():
    _save_states(14)
    scholarship = Scholarship.first(public_id=scholarship_id)
    college_id = scholarship.college.public_id

  response = client.get("/api/locations/states/13")

  assert response.status_code == 200
  state = response.get_json()["state"]

  response = client.get(state["_links"]["consolidated_cities"])
  assert response.status_code == 200

  consolidated_cities = response.get_json()["consolidated_cities"]["items"]

  response = client.post(
      f"/api/colleges/{college_id}/consolidated_cities",
      json={
          "location_fips": [
              consolidated_cities[0]["fips_code"],
              consolidated_cities[1]["fips_code"]
          ]
      })

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  response = client.get(f"/api/colleges/{college_id}/consolidated_cities")

  assert response.status_code == 200
  consolidated_cities_response = response.get_json()["consolidated_cities"][
      "items"]

  assert [
      consolidated_cities_response[0]["fips_code"],
      consolidated_cities_response[1]["fips_code"]
  ] == [
      consolidated_cities[0]["fips_code"], consolidated_cities[1]["fips_code"]
  ]

  response = client.post(
      f"/api/scholarships/{scholarship_id}/consolidated_cities",
      json={
          "location_fips": [
              consolidated_cities[0]["fips_code"],
              consolidated_cities[1]["fips_code"]
          ]
      })

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  response = client.get(
      f"/api/scholarships/{scholarship_id}/consolidated_cities")

  assert response.status_code == 200
  consolidated_cities_response = response.get_json()["consolidated_cities"][
      "items"]

  assert [
      consolidated_cities_response[0]["fips_code"],
      consolidated_cities_response[1]["fips_code"]
  ] == [
      consolidated_cities[0]["fips_code"], consolidated_cities[1]["fips_code"]
  ]
