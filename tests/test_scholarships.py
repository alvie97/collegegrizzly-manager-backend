from marshmallow import pprint
def test_post_scholarship(client):
    cr = client.post("/api/colleges", json={"name": "college test"})
    assert cr.status_code == 200
    data = cr.get_json()
    result = client.post(
        "/api/colleges/" + data["college_id"] + "/scholarships",
        json={"name": "test scholarship"})
    pprint(result.get_json())
    assert result.status_code == 200
