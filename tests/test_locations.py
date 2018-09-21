from app.models.college import College
from app.models.consolidated_city import ConsolidatedCity
from app.models.county import County
from app.models.place import Place
from app.models.scholarship import Scholarship
from app.models.state import State
from app.cli import _save_in_database


def test_location_requirements(app, client, scholarship_id):
  with app.app_context():
    _save_in_database()
    scholarship = Scholarship.first(public_id=scholarship_id)
    college_id = scholarship.college.public_id

  response = client.get("/locations/states/search/alabama")
  
  assert response.status_code == 200
  alabama = response.get_json()["state"]
  assert alabama["name"] == "Alabama"
  assert "fips_code" in alabama

  response = client.post(
      f"/colleges/{college_id}/states", json={"location_fips": [alabama["fips_code"]]})

  assert response.status_code == 200
  assert response.get_json()["message"] == "Locations added"

  with app.app_context():
    college = College.first(public_id=college_id)
    state = college.location_requirement_states.first()
    assert state.fips_code == alabama["fips_code"]
