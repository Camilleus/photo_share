from unittest.mock import patch

from src.services.auth import auth_service
from src.tests.conftest import login_user_token_created


def test_get_all_comments_for_picture_if_found(session, client):
    response = client.get("api/comments/", params={"picture_id": 1})

    assert response.status_code == 200, response.text
    data = response.json()
    assert data == [{"content": "test content 3", "updated_at": None, "id": 3, "user_id": 1, "picture_id": 1,
                                "created_at": "2024-03-12T21:49:38.921709"},
                               {"content": "test content 1", "updated_at": None, "id": 1, "user_id": 1, "picture_id": 1,
                                "created_at": "2024-03-12T21:42:38.921709"},
                               {"content": "test content 2", "updated_at": None, "id": 2, "user_id": 1, "picture_id": 1,
                                "created_at": "2024-03-12T21:40:38.921709"}]


def test_get_all_comments_for_picture_if_not_found(session, client):
    response = client.get("api/comments/", params={"picture_id": 2})

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_get_comment_if_found(session, client, user):
    new_user = login_user_token_created(user, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get("api/comments/1", headers={"accept": "application/json",
                                                         "Authorization": f"Bearer {new_user['access_token']}"
                                                         }, params={"comment_id": 1})

        assert response.status_code == 200, response.text
        data = response.json()
        assert data == {"content": "test content 1", "id": 1, "user_id": 1, "picture_id": 1,
                                   "created_at": "2024-03-12T21:42:38.921709", "updated_at": None}


def test_get_comment_if_not_found(session, client, user):
    new_user = login_user_token_created(user, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get("api/comments/4", headers={"accept": "application/json",
                                                         "Authorization": f"Bearer {new_user['access_token']}"
                                                         }, params={"comment_id": 4})

        assert response.status_code == 404, response.text
        data = response.json()
        assert data == {"detail": "Comment not found"}


def test_create_comment(session, client, user):
    new_user = login_user_token_created(user, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.post("api/comments/", headers={"accept": "application/json",
                                                         "Authorization": f"Bearer {new_user['access_token']}"
                                                         }, json={"content": "test content"}, params={"picture_id": 1})

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["content"] == "test content"


def test_update_comment_if_found(session, client, user):
    new_user = login_user_token_created(user, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.put("api/comments/1", headers={"accept": "application/json",
                                                         "Authorization": f"Bearer {new_user['access_token']}"
                                                         }, json={"content": "new content"}, params={"comment_id": 1})

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["content"] == "new content"


def test_update_comment_if_not_found(session, client, user):
    new_user = login_user_token_created(user, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.put("api/comments/4", headers={"accept": "application/json",
                                                         "Authorization": f"Bearer {new_user['access_token']}"
                                                         }, json={"content": "new content"}, params={"comment_id": 4})

        assert response.status_code == 404, response.text
        data = response.json()
        assert data == {"detail": "Comment not found"}


def test_delete_comment_if_admin(session, client, admin):
    new_user = login_user_token_created(admin, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.delete("api/comments/1", headers={"accept": "application/json",
                                                            "Authorization": f"Bearer {new_user['access_token']}"
                                                            }, params={"comment_id": 1})

        assert response.status_code == 200, response.text
        data = response.json()
        assert data == {"message": "The comment deleted successfully"}


def test_delete_comment_not_found_if_admin_(session, client, admin):
    new_user = login_user_token_created(admin, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.delete("api/comments/4", headers={"accept": "application/json",
                                                            "Authorization": f"Bearer {new_user['access_token']}"
                                                            }, params={"comment_id": 4})

        assert response.status_code == 403, response.text
        data = response.json()
        assert data == {"message": "The comment doesn't exist."}


def test_delete_comment_if_user(session, client, user):
    new_user = login_user_token_created(user, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.delete("api/comments/1", headers={"accept": "application/json",
                                                            "Authorization": f"Bearer {new_user['access_token']}"
                                                            }, params={"comment_id": 1})

        assert response.status_code == 403, response.text
        data = response.json()
        assert data == {"detail": "You don't have permission to perform this action."}

