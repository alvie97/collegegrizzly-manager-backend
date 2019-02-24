from app import db
from app.models.user import User

url = "/api/users"


def test_crud_users(app, client, auth):
    """ create, read, update and delete users """
    user_admin = {
        "username": "test_administrator",
        "email": "admin@gmail.com",
        "password": "123456",
        "role": "administrator"
    }

    user_moderator = {
        "username": "test_moderator",
        "email": "moderator@gmail.com",
        "password": "123456",
        "role": "moderator"
    }

    user_basic = {
        "username": "test_basic",
        "email": "basic@gmail.com",
        "password": "123456",
        "role": "basic"
    }

    auth.login()

    client.post(url, json=user_admin)
    client.post(url, json=user_moderator)
    client.post(url, json=user_basic)

    response = client.get(url)

    users = response.get_json()["items"]

    assert len(users) == 3

    assert users[0]["username"] == user_admin["username"]
    assert users[0]["role"] == user_admin["role"]
    assert users[1]["username"] == user_moderator["username"]
    assert users[1]["role"] == user_moderator["role"]
    assert users[2]["username"] == user_basic["username"]
    assert users[2]["role"] == user_basic["role"]

    response = client.get(url + f"/{user_admin['username']}")
    user = response.get_json()["user"]

    assert user["username"] == user_admin["username"]
    assert user["role"] == user_admin["role"]

    response = client.get(url + f"/{user_moderator['username']}")
    user = response.get_json()["user"]

    assert user["username"] == user_moderator["username"]
    assert user["role"] == user_moderator["role"]

    response = client.get(url + f"/{user_basic['username']}")
    user = response.get_json()["user"]

    assert user["username"] == user_basic["username"]
    assert user["role"] == user_basic["role"]

    client.patch(
        url + f"/{user_basic['username']}", json={"role": "administrator"})

    response = client.get(url + f"/{user_basic['username']}")
    user = response.get_json()["user"]

    assert user["username"] == user_basic["username"]
    assert user["role"] == "administrator"

    client.delete(url + f"/{user_basic['username']}")

    response = client.get(url)

    users = response.get_json()["items"]

    assert len(users) == 2

    assert users[0]["username"] == user_admin["username"]
    assert users[0]["role"] == user_admin["role"]
    assert users[1]["username"] == user_moderator["username"]
    assert users[1]["role"] == user_moderator["role"]


def test_user_role_protected_routes(app, client):
    """ test routes protected by user roles """

    user_admin = {
        "username": "test_administrator",
        "email": "admin@gmail.com",
        "password": "123456",
        "role": "administrator"
    }

    user_moderator = {
        "username": "test_moderator",
        "email": "moderator@gmail.com",
        "password": "123456",
        "role": "moderator"
    }

    user_basic = {
        "username": "test_basic",
        "email": "basic@gmail.com",
        "password": "123456",
        "role": "basic"
    }

    with app.app_context():

        user = User(**user_admin)
        db.session.add(user)

        user = User(**user_moderator)
        db.session.add(user)

        user = User(**user_basic)
        db.session.add(user)

        db.session.commit()

    # try only admin role routes

    client.post(
        "/auth/login",
        data={
            "id": user_admin["username"],
            "password": user_admin["password"]
        })

    response = client.get("/api/users")

    assert response.status_code == 200

    client.post("/auth/logout", headers={"X-XSRF-TOKEN": ""})

    client.post(
        "/auth/login",
        data={
            "id": user_moderator["username"],
            "password": user_moderator["password"]
        })

    response = client.get("/api/users")

    assert response.status_code == 403

    client.post("/auth/logout", headers={"X-XSRF-TOKEN": ""})

    client.post(
        "/auth/login",
        data={
            "id": user_basic["username"],
            "password": user_basic["password"]
        })

    response = client.get("/api/users")

    assert response.status_code == 403

    client.post("/auth/logout", headers={"X-XSRF-TOKEN": ""})

    # try routes protected from moderator role

    client.post(
        "/auth/login",
        data={
            "id": user_admin["username"],
            "password": user_admin["password"]
        })

    response = client.post("/api/colleges", json={"name": "test college"})

    assert response.status_code == 200

    client.post("/auth/logout", headers={"X-XSRF-TOKEN": ""})

    client.post(
        "/auth/login",
        data={
            "id": user_moderator["username"],
            "password": user_moderator["password"]
        })

    response = client.post("/api/colleges", json={"name": "test college"})

    assert response.status_code == 403

    client.post("/auth/logout", headers={"X-XSRF-TOKEN": ""})

    client.post(
        "/auth/login",
        data={
            "id": user_basic["username"],
            "password": user_basic["password"]
        })

    response = client.post("/api/colleges", json={"name": "test college"})

    assert response.status_code == 200

    client.post("/auth/logout", headers={"X-XSRF-TOKEN": ""})
