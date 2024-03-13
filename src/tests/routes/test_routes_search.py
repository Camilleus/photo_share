import pytest
import unittest

import pytest
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock
from fastapi import FastAPI, HTTPException, Depends
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json
from typing import Optional, List
from datetime import datetime

from src.routes.search import search_users, search_users_by_picture
from src.services.search import PictureSearchService
from src.database.models import Picture, User, Tag
from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch
from src.tests.conftest import TestingSessionLocal
from src.tests.conftest import login_user_token_created




def test_search_pictures(search_params, sort_by, sort_order, db):
    picture_search_service = PictureSearchService(db)
    pictures = picture_search_service.search_pictures(search_params, sort_by, sort_order)
    assert isinstance(pictures, List)
    for picture in pictures:
        assert isinstance(picture, PictureResponse)
        
        
def test_search_pictures(picture_s, user_s, admin, session, client):
    user_1 = login_user_token_created(user_s, session)
    user_2 = login_user_token_created(admin, session)

    picture = picture_s

    response = client.post(
        "/api/search/pictures",
        headers={"Authorization": f"Bearer {user_1.get('access_token')}"},
        json={"picture_id": 1,
              "rating": 3}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == [{'type': 'enum',
                               'loc': ['body', 'rating'],
                               'msg': 'Input should be 1, 2, 3, 4 or 5',
                               'input': 3,
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





def test_search_users(picture_s, user_s, admin, session, client):
    user_1 = login_user_token_created(user_s, session)
    user_2 = login_user_token_created(admin, session)
    
    user = user_s
    
    
    
    
def test_search_users_by_picture(picture_s, user_s, admin, session, client):
    user_1 = login_user_token_created(user_s, session)
    user_2 = login_user_token_created(admin, session)
    
    user = user_s
    
    
    
    
    
# import pytest
# import unittest
# from fastapi import HTTPException
# from fastapi.testclient import TestClient
# from sqlalchemy.orm import Session
# import json
# from datetime import datetime

# from src.routes.search import search_users, search_users_by_picture
# from src.database.models import Picture, User, Tag
# from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch
# from src.tests.conftest import TestingSessionLocal, client


# #Create test data
# def create_test_data():
#     db = TestingSessionLocal()

#     picture1 = Picture(
#         title="Test Picture 1",
#         description="This is a test picture.",
#         rating=5,
#         created_at=datetime.datetime.utcnow(),
#     )

#     picture2 = Picture(
#         title="Test Picture 2",
#         description="This is another test picture.",
#         rating=3,
#         created_at=datetime.datetime.utcnow(),
#     )

#     tag1 = Tag(name="test_tag1")
#     tag2 = Tag(name="test_tag2")

#     picture1.tags = [tag1, tag2]
#     picture2.tags = [tag2]

#     db.add(picture1)
#     db.add(picture2)
#     db.add(tag1)
#     db.add(tag2)

#     db.commit()
#     db.refresh(picture1)
#     db.refresh(picture2)
#     db.refresh(tag1)
#     db.refresh(tag2)

#     db.close()

# create_test_data()





#Test cases for search pictures
# class TestPictureSearch(unittest.TestCase):
    
#     def test_search_pictures_by_keywords(self):
#         response = client.get(
#             "/search/pictures",
#             params={"keywords": "test"},
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 1)
#         self.assertEqual(response.json()[0]["title"], "Test Picture 1")

#     def test_search_pictures_by_tags(self):
#         response = client.get(
#             "/search/pictures",
#             params={"tags": "test_tag1"},
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 1)
#         self.assertEqual(response.json()[0]["title"], "Test Picture 1")

#     def test_search_pictures_by_rating(self):
#         response = client.get(
#             "/search/pictures",
#             params={"rating": "3"},
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 1)
#         self.assertEqual(response.json()[0]["title"], "Test Picture 2")

                
#     def test_search_pictures_with_picture_name_filter(self):
#         response = client.get(
#             "/search/pictures",
#             params={"title": "Test Picture 2"},
#         )

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(response.json()), 1)
#         self.assertEqual(response.json()[0]["title"], "Test Picture 2")