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