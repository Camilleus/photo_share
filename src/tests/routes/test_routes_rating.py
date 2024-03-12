from src.tests.conftest import login_user_token_created


def test_routes_rating(user, admin, picture_s, session, client):
    user_1 = login_user_token_created(user, session)
    user_2 = login_user_token_created(admin, session)

    picture = picture_s

    response = client.post(
        "/api/rating/",
        headers={"Authorization": f"Bearer {user_1.get('access_token')}"},
        json={"picture_id": 1,
              "rating": 7}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == [{'type': 'enum',
                               'loc': ['body', 'rating'],
                               'msg': 'Input should be 1, 2, 3, 4 or 5',
                               'input': 7,
                               'ctx': {'expected': '1, 2, 3, 4 or 5'}}]


    response = client.post(
        "/api/rating/",
        headers={"Authorization": f"Bearer {user_1.get('access_token')}"},
        json={"picture_id": 1,
              "rating": 3}
    )

    assert response.status_code == 201
    assert response.json() == {"message": "The rating was successfully created or updated."}

    response = client.post(
        "/api/rating/",
        headers={"Authorization": f"Bearer {user_1.get('access_token')}"},
        json={"picture_id": 1,
              "rating": 5}
    )

    assert response.status_code == 201
    assert response.json() == {"message": "The rating was successfully created or updated."}

    response = client.post(
        "/api/rating/",
        headers={"Authorization": f"Bearer {user_2.get('access_token')}"},
        json={"picture_id": 1,
              "rating": 2}
    )

    assert response.status_code == 201
    assert response.json() == {"message": "The rating was successfully created or updated."}

    response = client.post(
        "/api/rating/picture",
        json={"picture_id": 1}
    )

    assert response.status_code == 200
    assert response.json() == {"1": 5, "99": 2}

    response = client.post(
        "/api/rating/average/picture",
        json={"picture_id": 1}
    )

    assert response.status_code == 200
    assert response.json() == {"average_rating": 3.5}

    response = client.post(
        "/api/rating/average/picture",
        json={"picture_id": 2}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "No ratings available for this picture."}

    response = client.delete(
        "/api/rating/1",
        headers={"Authorization": f"Bearer {user_1.get('access_token')}"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Rating removed successfully."}

    response = client.delete(
        "/api/rating/1",
        headers={"Authorization": f"Bearer {user_1.get('access_token')}"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "No rating found for this user and picture."}

