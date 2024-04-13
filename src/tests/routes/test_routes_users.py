from src.tests.conftest import login_user_confirmed_true_and_hash_password, login_user_token_created


def test_read_users_me(user, session, client):
    token_user = login_user_token_created(user, session)

    response = client.get('/api/users/me/',
                          headers={'Authorization': f'Bearer {token_user.get("access_token")}'},
                          )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email


def test_update_avatar_user(user, session, client, monkeypatch, mock_picture):
    new_user = login_user_token_created(user, session)

    mock_uploaded_file = {"file": ("test_image.png", mock_picture, "image/png")}

    response = client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {new_user.get('access_token')}"},
        files=mock_uploaded_file
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert "created_at" in data
    assert "avatar" in data


def test_list_all_users_user(client, user, session):
    login_user_confirmed_true_and_hash_password(user, session)
    response = client.get("/api/users/all")

    assert response.status_code == 401

def test_list_all_users_admin(client, admin,  session):
    token_details = login_user_token_created(admin, session)

    response = client.get("/api/users/all", headers={"Authorization": f"Bearer {token_details['access_token']}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_update_user_name(client, user, session):
    login_user_confirmed_true_and_hash_password(user, session)

    new_username = "new_example"
    user_id = 1

    response = client.patch(f"/api/users/update/{user_id}", json={"username": new_username})

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == new_username



def test_read_user_by_username(user, session, client):
    login_user_confirmed_true_and_hash_password(user, session)

    response = client.get(f"/api/users/name/{user.username}")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email


def test_read_nonexistent_user_by_username(client):
    user_name = "nonexistent_user"

    response = client.get(f"/api/users/name/{user_name}")

    assert response.status_code == 404
