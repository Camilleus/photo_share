import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime

from main import app
from src.database.models import Picture
from src.services.auth import auth_service
from src.tests.conftest import login_user_token_created, login_user_token_created_unconfirmed

client = TestClient(app)


def create_x_pictures(session, no_of_pictures):
    pictures = []
    for i in range(no_of_pictures):
        picture = Picture(picture_url=f"test_url{i}", description=f"test_description{i}", created_at=datetime.now())
        session.add(picture)
        session.commit()
        pictures.append(picture)
    return pictures


def test_upload_description_picture_found(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_upload = no_of_pictures - 1

    pictures = create_x_pictures(session, no_of_pictures)

    new_description = "Test of description uploading"

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            f"/api/descriptions/upload/",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            params={"picture_id": no_to_upload, "description": new_description},
        )
        data = response.json()

        assert response.status_code == 201, response.text
        assert data["description"] == new_description


def test_upload_description_picture_found_unauthorized(user, session, client):
    new_user = login_user_token_created_unconfirmed(user, session)
    no_of_pictures = 4
    no_to_upload = no_of_pictures - 1

    pictures = create_x_pictures(session, no_of_pictures)

    new_description = "Test of description uploading"

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            f"/api/descriptions/upload/",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            params={"picture_id": no_to_upload, "description": new_description},
        )

        assert response.status_code == 401, response.text


def test_upload_description_picture_not_found(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_upload = no_of_pictures + 100

    pictures = create_x_pictures(session, no_of_pictures)

    new_description = "Test of description uploading"

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            f"/api/descriptions/upload/",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            params={"picture_id": no_to_upload, "description": new_description},
        )
        data = response.json()

        assert response.status_code == 404, response.text


def test_get_all_descriptions(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    pictures = create_x_pictures(session, no_of_pictures)
    list_of_descriptions = []
    for i in range(no_of_pictures):
        list_of_descriptions.append(pictures[i].description)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/descriptions/",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )
        data = response.json()

        assert response.status_code == 200, response.text
        assert isinstance(data, list)
        assert len(data) == no_of_pictures
        for i in range(no_of_pictures):
            assert data[i]["description"] == list_of_descriptions[i]


def test_get_all_descriptions_unauthorized(user, session, client):
    new_user = login_user_token_created_unconfirmed(user, session)
    no_of_pictures = 4
    pictures = create_x_pictures(session, no_of_pictures)
    list_of_descriptions = []
    for i in range(no_of_pictures):
        list_of_descriptions.append(pictures[i].description)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/descriptions/",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )

        assert response.status_code == 401, response.text


def test_get_one_description_picture_found(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_get = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)
    description = pictures[no_to_get - 1].description

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/descriptions/{no_to_get}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            )
        data = response.json()

        assert response.status_code == 200, response.text
        assert data["description"] == description


def test_get_one_description_picture_found_unauthorized(user, session, client):
    new_user = login_user_token_created_unconfirmed(user, session)
    no_of_pictures = 4
    no_to_get = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)
    description = pictures[no_to_get - 1].description

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/descriptions/{no_to_get}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            )

        assert response.status_code == 401, response.text



def test_get_one_description_picture_not_found(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_get = no_of_pictures + 100
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"api/descriptions/{no_to_get}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )

        assert response.status_code == 404, response.text


def test_update_description_picture_found(admin, session, client):
    new_user = login_user_token_created(admin, session)
    no_of_pictures = 4
    no_to_update = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    updated_description = "Test of updating description"

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/descriptions/{no_to_update}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            params={"new_description": updated_description},
        )
        data = response.json()

        assert response.status_code == 200, response.text
        assert data["description"] == updated_description


def test_update_description_picture_found_unauthorized(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_update = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    updated_description = "Test of updating description"

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/descriptions/{no_to_update}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            params={"new_description": updated_description},
        )
        data = response.json()

        assert response.status_code == 403, response.text


def test_update_description_picture_not_found(admin, session, client, mock_picture):
    new_user = login_user_token_created(admin, session)
    updated_description = "Test of updating description"
    no_of_pictures = 4
    no_to_update = no_of_pictures + 100
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/descriptions/{no_to_update}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            params={"new_description": updated_description},
        )
        assert response.status_code == 404, response.text


def test_delete_description_picture_found(admin, session, client):
    new_user = login_user_token_created(admin, session)
    no_of_pictures = 4
    no_to_delete = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/descriptions/{no_to_delete}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            }
        )
        data = response.json()

        assert response.status_code == 200, response.text
        assert data["description"] == None


def test_delete_description_picture_found_unauthorized(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_delete = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/descriptions/{no_to_delete}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            }
        )
        data = response.json()

        assert response.status_code == 403, response.text


def test_delete_description_picture_not_found(admin, session, client):
    new_user = login_user_token_created(admin, session)
    no_of_pictures = 4
    no_to_delete = no_of_pictures + 100
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/descriptions/{no_to_delete}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            }
        )
        assert response.status_code == 404, response.text
