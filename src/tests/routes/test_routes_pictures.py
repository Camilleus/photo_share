import pytest

from unittest.mock import patch, MagicMock
from datetime import datetime

from src.database.models import Picture
from src.services.auth import auth_service
from src.tests.conftest import login_user_token_created, login_user_token_created_unconfirmed
from src.routes import pictures



def create_x_pictures(session, no_of_pictures):
    pictures = []
    for i in range(no_of_pictures):
        picture = Picture(picture_url=f"test_url{i}",
                          description=f"test_description{i}",
                          created_at=datetime.now(),
                          qr_code_picture=f"test_qr_code{i}")
        session.add(picture)
        session.commit()
        pictures.append(picture)
    return pictures


def test_upload_picture(user, session, client, mock_picture):
    new_user = login_user_token_created(user, session)

    mock_picture1 = {"picture": ("test_image.png", mock_picture, "image/png")}

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/pictures/upload",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            files=mock_picture1,
        )
        data = response.json()

        assert response.status_code == 201, response.text
        assert "id" in data
        assert "picture_url" in data
        assert "qr_code_picture" in data
        assert "created_at" in data


def test_upload_picture_unauthorized(user, session, client, mock_picture):
    new_user = login_user_token_created_unconfirmed(user, session)

    mock_picture1 = {"picture": ("test_image.png", mock_picture, "image/png")}

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/pictures/upload",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            files=mock_picture1,
        )

        assert response.status_code == 401, response.text


def test_get_all_pictures(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/pictures/",
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
            assert data[i]["id"] == pictures[i].id
            assert data[i]["picture_url"] == pictures[i].picture_url
            assert data[i]["description"] == pictures[i].description
            assert "created_at" in data[i]


def test_get_one_picture_found(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_get = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/pictures/{no_to_get}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )
        data = response.json()

        assert response.status_code == 200, response.text
        assert data["id"] == pictures[no_to_get-1].id
        assert data["picture_url"] == pictures[no_to_get - 1].picture_url
        assert data["description"] == pictures[no_to_get - 1].description
        assert "created_at" in data


def test_get_one_picture_found_unauthorized(user, session, client):
    new_user = login_user_token_created_unconfirmed(user, session)
    no_of_pictures = 4
    no_to_get = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/pictures/{no_to_get}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )

        assert response.status_code == 401, response.text


def test_get_one_picture_not_found(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_get = no_of_pictures + 100
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"api/pictures/{no_to_get}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )

        assert response.status_code == 404, response.text


def test_update_picture_found(admin, session, client, mock_picture):
    new_user = login_user_token_created(admin, session)
    mock_picture1 = {"picture": ("test_image.png", mock_picture, "image/png")}
    no_of_pictures = 4
    no_to_update = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/pictures/{no_to_update}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            files=mock_picture1
        )

        data = response.json()

        assert response.status_code == 200, response.text
        assert "id" in data
        assert "picture_url" in data
        assert "created_at" in data


def test_update_picture_found_unauthorized(user, session, client, mock_picture):
    new_user = login_user_token_created(user, session)
    mock_picture1 = {"picture": ("test_image.png", mock_picture, "image/png")}
    no_of_pictures = 4
    no_to_update = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/pictures/{no_to_update}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            files=mock_picture1,
        )

        assert response.status_code == 403, response.text


def test_update_picture_not_found(admin, session, client, mock_picture):
    new_user = login_user_token_created(admin, session)
    mock_picture1 = {"picture": ("test_image.png", mock_picture, "image/png")}
    no_of_pictures = 4
    no_to_update = no_of_pictures + 100
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/pictures/{no_to_update}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
            files=mock_picture1,
        )

        assert response.status_code == 404, response.text


def test_delete_picture_found(admin, session, client):
    new_user = login_user_token_created(admin, session)
    no_of_pictures = 4
    no_to_delete = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/pictures/{no_to_delete}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )
        data = response.json()

        assert response.status_code == 200, response.text
        assert "id" in data
        assert "picture_url" in data
        assert "created_at" in data


def test_delete_picture_found_unauthorized(user, session, client):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_delete = no_of_pictures - 1
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/pictures/{no_to_delete}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )

        assert response.status_code == 403, response.text


def test_delete_picture_not_found(admin, session, client):
    new_user = login_user_token_created(admin, session)
    no_of_pictures = 4
    no_to_delete = no_of_pictures + 100
    pictures = create_x_pictures(session, no_of_pictures)

    with patch.object(auth_service, 'r') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/pictures/{no_to_delete}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )

        assert response.status_code == 404, response.text

@pytest.mark.asyncio
async def test_edit_picture(admin, session, client):
    new_user = login_user_token_created(admin, session)

    picture_id = 1
    picture_edit = MagicMock()
    picture_edit.improve = "0"
    picture_edit.contrast = "0"
    picture_edit.unsharp_mask = "500"
    picture_edit.brightness = "10"
    picture_edit.gamma = "50"
    picture_edit.grayscale = False
    picture_edit.redeye = False
    picture_edit.gen_replace = "from_null;to_null"
    picture_edit.gen_remove = "prompt_null"
    picture_mock = MagicMock()
    picture_mock.picture_json = {"public_id": "public_id", "version": "version"}

    with patch.object(auth_service, 'r') as r_mock, \
        patch("src.routes.pictures.repository_pictures.get_one_picture", return_value=picture_mock) as mock_get_one_picture, \
        patch("src.routes.pictures.cloudinary.uploader.upload") as mock_cloudinary_upload, \
        patch("src.routes.pictures.generate_qr_and_upload_to_cloudinary") as mock_generate_qr_and_upload, \
        patch("src.routes.pictures.cloudinary.CloudinaryImage") as mock_cloudinary_image:

        r_mock.get.return_value = None
        response = client.post(
            "/api/pictures/edit/{picture_id}",
            headers={
                'accept': 'application/json',
                "Authorization": f"Bearer {new_user['access_token']}"
            },
        )

        expected_edited_data = {
            "public_id": "edited_public_id",
            "version": "edited_version",
            "url": "https://res.cloudinary.com/dummy/image/upload/vedited_version/edited_public_id"
        }
        expected_edited_url = "https://res.cloudinary.com/dummy/image/upload/vedited_version/edited_public_id"
        expected_qr_url = "https://res.cloudinary.com/dummy/image/upload/qrcode/edited_qr"

        mock_picture_upload = MagicMock(return_value=expected_edited_data)
        mock_build_url = MagicMock(return_value=expected_edited_url)
        mock_qr_upload = MagicMock(return_value=expected_qr_url)

        mock_cloudinary_upload.side_effect = mock_picture_upload
        mock_generate_qr_and_upload.side_effect = mock_qr_upload
        mock_cloudinary_image.return_value.build_url = mock_build_url

        edited_picture = await pictures.edit_picture(picture_id, picture_edit, admin, db=session)

    assert edited_picture == {
        "picture_edited_url": expected_edited_url,
        "qr_code_picture_edited": expected_qr_url
    }
    assert response.status_code == 422, response.text
