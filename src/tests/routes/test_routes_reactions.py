from unittest.mock import patch

from src.database.models import User
from src.services.auth import auth_service
from src.tests.conftest import login_user_token_created


def test_get_all_reactions_for_comment(session, client):
    user = User(id=1, username="test name", email="example@test.pl", password="secret")
    session.add(user)
    session.commit()
    response = client.get("api/reactions/1", params={"comment_id": 1})
    assert response.status_code == 200, response.text
    print(response.json())
    assert response.json() == {"test name": "like"}


def test_get_number_reactions_for_comment_(session, client):
    response = client.get("api/reactions/number/2", params={"picture_id": 2})
    assert response.status_code == 200, response.text
    assert response.json() == {'haha': 5, 'like': 3, 'wow': 2}


def test_add_reaction(session, client, user):
    new_user = login_user_token_created(user, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.post("api/reactions/like", headers={"accept": "application/json",
                                                              "Authorization": f"Bearer {new_user['access_token']}"
                                                              }, params={"comment_id": 2, "reaction": "wow"})
        data = response.json()
        print(data)
        assert response.status_code == 201, response.text
        assert data == {"message": "The reaction was added"}


def test_delete_reaction_if_found(session, client, user):
    new_user = login_user_token_created(user, session)
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.delete("api/reactions/like", headers={"accept": "application/json",
                                                                "Authorization": f"Bearer {new_user['access_token']}"
                                                                }, params={"comment_id": 1})
        data = response.json()
        assert response.status_code == 200, response.text
        assert data == {"message": "Reaction was deleted"}
