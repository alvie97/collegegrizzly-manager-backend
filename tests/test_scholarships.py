from marshmallow import pprint
from app.models.scholarship import Scholarship

def test_get_scholarships(client, college_id):

  assert client.get("/api/colleges/" + college_id).status_code == 200

def test_post_scholarship(client, college_id):
    result = client.post(
        "/api/colleges/" + college_id +  "/scholarships",
        json={"name": "test scholarship"})

    assert result.status_code == 200

def test_update_scholarship(app, client, scholarship_id):

  result = client.put(
    "/api/scholarships/" + scholarship_id,
    json={"description": "this is an updated description"})

  assert result.status_code == 200

  with app.app_context():
    scholarship = Scholarship.first(public_id=scholarship_id)

    assert scholarship.description == "this is an updated description"

def test_delete_scholarship(app, client, scholarship_id):

  result = client.delete("/api/scholarships/" + scholarship_id)

  assert result.status_code == 200

  with app.app_context():
    scholarship = Scholarship.first(public_id=scholarship_id)

    assert scholarship is None
