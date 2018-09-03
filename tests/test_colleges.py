# import pytest

def test_get_colleges(client):
  assert client.get("/api/colleges").status_code == 200
