import pytest
import json
import unittest
from datetime import datetime

from src.tests.conftest import engine, Base, TestingSessionLocal
from src.database.models import Base, Picture, User
from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch
from main import app


def user_s():
    class UserTest:
        def __init__(self, id, username, email):
            self.id = id
            self.username = username
            self.email = email

        def dict(self):
            return {
                "id": self.id,
                "username": self.username,
                "email": self.email
            }
    return UserTest(
                    id=1,
                    username="example",
                    email="example@example.com"
                    )
    
    
def picture_s():
    class PictureTest:
        def __init__(self, id, user_id, rating, tags, picture_name, picture_url, created_at):
            self.id = id
            self.user_id = user_id
            self.rating = rating
            self.tags = tags
            self.picture_name = picture_name
            self.picture_url = picture_url
            self.created_at = created_at


        def dict(self):
            return {
                "id": self.id,
                "user_id": self.user_id,
                "rating": self.rating,
                "tags": self.tags,
                "picture_name": self.picture_name,
                "created_at": self.created_at
            }
    return PictureTest(
                    id=1,
                    user_id=1,
                    rating=4,
                    tags=['picture_tag', 'picture_tag2'],
                    picture_name=f"picture{id}_name",
                    picture_url=f"picture{id}_url",
                    created_at=datetime.now()
                    )
    

def fake_db_for_search_test():
    '''
    This fixture is used to fake db for search testing
    '''
    db = {"pictures": {}, "users": {}, "next_picture_id": 1, "next_user_id": 1}
    def create_picture(user_id, rating, tags, picture_name, picture_url, created_at):
        
            picture_id = db["next_picture_id"]
            db["pictures"][picture_id] = {
                "id": picture_id,
                "user_id": user_id,
                "rating": rating,
                "tags": tags,
                "picture_name": picture_name,
                "picture_url": picture_url,
                "created_at": created_at
            }
            db["next_picture_id"] += 1
            picture = Picture(id=picture_id,user_id=user_id, rating=rating, tags=tags, picture_name=picture_name, picture_url=picture_url, created_at=created_at)
            db["pictures"][picture_id] = picture
            return picture

    db["create_picture"] = create_picture
    
    def create_user(email, username):
        user_id = db["next_user_id"]
        db["users"][user_id] = {
            "id": user_id,
            "email": email,
            "username": username
        }
        db["next_user_id"] += 1
        return db["users"][user_id]
    
    db["create_users"] = create_user
    return db


picture1 = picture_s(1, 3, ["picture1_tag", "picture1_tag2"], "picture1_name", "picture1_url", datetime.now)
picture2 = picture_s(2, 4, ["picture1_tag2", "picture1_tag3"], "picture2_name", "picture2_url", datetime.now)
picture3 = picture_s(3, 5, ["picture1_tag2", "picture1_tag3"], "picture3_name", "picture3_url", datetime.now)
picture4 = picture_s(4, 2, ["picture1_tag3", "picture1_tag4"], "picture4_name", "picture4_url", datetime.now)
picture5 = picture_s(5, 1, ["picture1_tag", "picture1_tag4"], "picture5_name", "picture5_url", datetime.now)
picture6 = picture_s(6, 2, ["picture1_tag1", "picture1_tag2"], "picture6_name", "picture6_url", datetime.now)
picture7 = picture_s(7, 3, ["picture1_tag1", "picture1_tag2"], "picture7_name", "picture7_url", datetime.now)
picture8 = picture_s(8, 4, ["picture1_tag2", "picture1_tag3"], "picture8_name", "picture8_url", datetime.now)
picture9 = picture_s(9, 5, ["picture1_tag3", "picture1_tag4"], "picture9_name", "picture9_url", datetime.now)
picture10 = picture_s(10, 1, ["picture1_tag", "picture1_tag4"], "picture10_name", "picture10_url", datetime.now)

pictures = [picture1, picture2, picture3, picture4, picture5, picture6, picture7, picture8, picture9, picture10]

user1 = user_s(1,f"test_email1",f"test_username1") 
user2 = user_s(2,f"test_email2",f"test_username2")
user3 = user_s(3,f"test_email3",f"test_username3")
user4 = user_s(4,f"test_email4",f"test_username4") 
user5 = user_s(5,f"test_email5",f"test_username5")
      
users = [user1, user2, user3, user4, user5]
    
@pytest.fixture(scope="function", autouse=True)
def setup_test_database(session, db):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        for picture in pictures:
            db.add(picture)

        for user in users:
            db.add(user)

        db.commit()
        yield db
    finally:
        db.rollback()
        db.close()


class TestPictureSearch(unittest.TestCase):
        
    def test_get_method(picture_s):
        # Test the .get method with a valid key
        picture = picture_s
        assert picture.get("id") == 1

        # Test the .get method with an invalid key
        assert picture.get("invalid_key") is None

        # Test the .get method with a valid key and a default value
        assert picture.get("id", "default_value") == 1
        assert picture.get("invalid_key", "default_value") == "default_value"
                
    def test_search_pictures_with_picture_name_filter(client, picture_s):
        # Set up the test data
        picture_name = picture_s().picture_name

        # Send the search request with the picture name filter
        response = client.post(f"/api/pictures/search?name={picture_name}")

        # Check the response status code
        assert response.status_code == 200

        # Check that the response contains the expected picture
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == picture_s().id
        
    def test_search_pictures_with_rating_filter(self):
         pass
                   
    def test_search_pictures_with_added_after_filter(self):
        pass
            
    def test_search_pictures_sorting(self):
        pass

    
class TestUserSearch(unittest.TestCase):
    
    def test_search_users_by_keyword(self):
        pass

    def test_search_users_by_username(self):
        pass

    def test_search_users_by_email(self):
        pass


class TestUserPictureSearch(unittest.TestCase):
    
    def test_search_users_by_pictures_by_keywords(self):
        pass

    def test_search_users_by_pictures_with_user_id_filter(self):
        pass
                
    def test_search_users_by_pictures_with_picture_id_filter(self):
        pass
                                
    def test_search_users_by_pictures_with_rating_filter(self):
        pass

    def test_search_users_by_pictures_with_added_after_filter(self):
        pass


if __name__ == "__main__":
    pytest.main()