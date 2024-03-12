import pytest
import unittest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from src.database.db import get_db
from src.database.models import Picture, Tag, User
from src.routes.auth import get_current_user
from src.tests.conftest import user_s, picture_s, TestingSessionLocal, Base, engine
from src.routes.search import search_users, search_users_by_picture
from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch

#Models for Search Testing
# @pytest.fixture
# def user_s():
#     class UserTest:
#         def __init__(self, id, username, email):
#             self.id = id
#             self.username = username
#             self.email = email

#         def dict(self):
#             return {
#                 "id": self.id,
#                 "username": self.username,
#                 "email": self.email
#             }
#     return UserTest(
#                     id=1,
#                     username="example",
#                     email="example@example.com"
#                     )
    
# @pytest.fixture
# def picture_s():
#     class PictureTest:
#         def __init__(self, id, user_id, rating, tags, picture_name, picture_url, created_at):
#             self.id = id
#             self.user_id = user_id
#             self.rating = rating
#             self.tags = tags
#             self.picture_name = picture_name
#             self.picture_url = picture_url
#             self.created_at = created_at


#         def dict(self):
#             return {
#                 "id": self.id,
#                 "user_id": self.user_id,
#                 "rating": self.rating,
#                 "tags": self.tags,
#                 "picture_name": self.picture_name,
#                 "created_at": self.created_at
#             }
#     return PictureTest(
#                     id=1,
#                     user_id=1,
#                     rating=4,
#                     tags=['picture_tag', 'picture_tag2'],
#                     picture_name=f"picture{id}_name",
#                     picture_url=f"picture{id}_url",
#                     created_at=datetime.now()
#                     )

# def fake_db_for_search_test():
#     '''
#     This fixture is used to fake db for search testing
#     '''
#     db = {"pictures": {}, "users": {}, "next_picture_id": 1, "next_user_id": 1}
#     def create_picture(user_id, rating, tags, picture_name, picture_url, created_at):
        
#             picture_id = db["next_picture_id"]
#             db["pictures"][picture_id] = {
#                 "id": picture_id,
#                 "user_id": user_id,
#                 "rating": rating,
#                 "tags": tags,
#                 "picture_name": picture_name,
#                 "picture_url": picture_url,
#                 "created_at": created_at
#             }
#             db["next_picture_id"] += 1
#             picture = Picture(id=picture_id,user_id=user_id, rating=rating, tags=tags, picture_name=picture_name, picture_url=picture_url, created_at=created_at)
#             db["pictures"][picture_id] = picture
#             return picture

#     db["create_picture"] = create_picture
    
#     def create_user(email, username):
#         user_id = db["next_user_id"]
#         db["users"][user_id] = {
#             "id": user_id,
#             "email": email,
#             "username": username
#         }
#         db["next_user_id"] += 1
#         return db["users"][user_id]
    
#     db["create_users"] = create_user
#     return db


# pictures = [
#     (1, 3, ["picture1_tag", "picture1_tag2"], "picture1_name", datetime.now),
#     (2, 4, ["picture1_tag2", "picture1_tag3"], "picture2_name", datetime.now),
#     (3, 5, ["picture1_tag2", "picture1_tag3"], "picture3_name", datetime.now),
#     (4, 2, ["picture1_tag3", "picture1_tag4"], "picture4_name", datetime.now),
#     (5, 1, ["picture1_tag", "picture1_tag4"], "picture5_name", datetime.now),
#     (6, 2, ["picture1_tag1", "picture1_tag2"], "picture6_name", datetime.now),
#     (7, 3, ["picture1_tag1", "picture1_tag2"], "picture7_name", datetime.now),
#     (8, 4, ["picture1_tag2", "picture1_tag3"], "picture8_name", datetime.now),
#     (9, 5, ["picture1_tag3", "picture1_tag4"], "picture9_name", datetime.now),
#     (10, 1, ["picture1_tag", "picture1_tag4"], "picture10_name", datetime.now)
# ]


# users = [
#     (1,f"test_email1",f"test_username1"), 
#     (2,f"test_email2",f"test_username2"), 
#     (3,f"test_email3",f"test_username3"), 
#     (4,f"test_email4",f"test_username4"), 
#     (5,f"test_email5",f"test_username5")
# ]       
    
# @pytest.fixture(scope="function", autouse=True)
# def setup_test_database(picture_s, user_s):
#     Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)

#     db = TestingSessionLocal()
#     try:
#         for picture in pictures:
#             p = picture_s(id=picture[0], user_id=picture[1], tags=picture[2], name=picture[3], created_at=picture[4])
#             db.add(p)

#         for user in users:
#             u = user_s(id=user[0], email=user[1], username=user[2])
#             db.add(u)

#         db.commit()
#         yield db
#     finally:
#         db.rollback()
#         db.close()




#Create test data
def create_test_data():
    db = TestingSessionLocal()

    picture1 = Picture(
        title="Test Picture 1",
        description="This is a test picture.",
        rating=5,
        created_at=datetime.datetime.utcnow(),
    )

    picture2 = Picture(
        title="Test Picture 2",
        description="This is another test picture.",
        rating=3,
        created_at=datetime.datetime.utcnow(),
    )

    tag1 = Tag(name="test")
    tag2 = Tag(name="picture")

    picture1.tags = [tag1, tag2]
    picture2.tags = [tag2]

    db.add(picture1)
    db.add(picture2)
    db.add(tag1)
    db.add(tag2)

    db.commit()
    db.refresh(picture1)
    db.refresh(picture2)
    db.refresh(tag1)
    db.refresh(tag2)

    db.close()

create_test_data()





#Test cases
def test_create_test_data():
    db = TestingSessionLocal()

    # Test that two pictures are created
    assert db.query(Picture).count() == 0
    create_test_data()
    assert db.query(Picture).count() == 2

    # Test that the pictures have the correct attributes
    picture1 = db.query(Picture).first()
    assert picture1.title == "Test Picture 1"
    assert picture1.description == "This is a test picture."
    assert picture1.rating == 5

    picture2 = db.query(Picture).second()
    assert picture2.title == "Test Picture 2"
    assert picture2.description == "This is another test picture."
    assert picture2.rating == 3

    # Test that two tags are created
    assert db.query(Tag).count() == 0
    create_test_data()
    assert db.query(Tag).count() == 2

    # Test that the tags have the correct attributes
    tag1 = db.query(Tag).first()
    assert tag1.name == "test"

    tag2 = db.query(Tag).second()
    assert tag2.name == "picture"

    # Test that the pictures have the correct tags
    picture1 = db.query(Picture).first()
    assert len(picture1.tags) == 2
    assert "test" in [tag.name for tag in picture1.tags]
    assert "picture" in [tag.name for tag in picture1.tags]

    picture2 = db.query(Picture).second()
    assert len(picture2.tags) == 1
    assert "picture" in [tag.name for tag in picture2.tags]

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
        
        
class Test_Search_Picture:

    # The function returns a list of PictureResponse objects when given valid search parameters.
    def test_valid_search_parameters(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

    # The function returns an empty list when given an empty search_params object.
    def test_empty_search_params(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = []

        # Call the search_pictures function with an empty search_params object
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is an empty list
        assert result == []

    # The function returns a list of PictureResponse objects when given valid search parameters and a valid database connection.
    def test_valid_search_parameters(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

    # The function returns a list of PictureResponse objects sorted by created_at in descending order by default.
    def test_default_sort_order(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function with default sort order
        result = self.search_pictures(PictureSearch())

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

        # Assert that the search_pictures method was called with the correct parameters
        mock_service.search_pictures.assert_called_once_with(PictureSearch(), "created_at", "desc")

    # The function returns a list of PictureResponse objects sorted by the specified sort_by parameter in the specified sort_order parameter.
    def test_search_pictures_sorting(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function with different sort_by and sort_order parameters
        result1 = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')
        result2 = self.search_pictures(PictureSearch(), sort_by='likes', sort_order='asc')
        result3 = self.search_pictures(PictureSearch(), sort_by='views', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result1, list)
        assert all(isinstance(picture, PictureResponse) for picture in result1)
        assert isinstance(result2, list)
        assert all(isinstance(picture, PictureResponse) for picture in result2)
        assert isinstance(result3, list)
        assert all(isinstance(picture, PictureResponse) for picture in result3)

        # Assert that the results are sorted correctly
        assert result1 == [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]
        assert result2 == [PictureResponse(id=2, url='example.com/pic2.jpg'), PictureResponse(id=1, url='example.com/pic1.jpg')]
        assert result3 == [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

    # The function returns an empty list when given valid search parameters but an invalid database connection.
    def test_invalid_database_connection(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method to raise an exception
        mock_service.search_pictures.side_effect = Exception("Invalid database connection")

        # Call the search_pictures function
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is an empty list
        assert result == []

    # The function returns an empty list when no pictures match the search parameters.
    def test_empty_list_returned_when_no_pictures_match_search_parameters(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method to return an empty list
        mock_service.search_pictures.return_value = []

        # Call the search_pictures function with search parameters that don't match any pictures
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is an empty list
        assert result == []

    # The function can handle search_params with multiple fields set to the same value.
    def test_handle_multiple_fields_same_value(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function with search_params having multiple fields set to the same value
        search_params = PictureSearch(field1="value", field2="value", field3="value")
        result = self.search_pictures(search_params, sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

    # The function can handle large amounts of data without crashing or running out of memory.
    def test_handle_large_amounts_of_data(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

    # The function returns an empty list when given search_params with all fields set to empty strings.
    def test_empty_search_params(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Call the search_pictures function with empty search_params
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is an empty list
        assert result == []

    # The function can handle search_params with multiple fields set to different values.
    def test_handle_multiple_fields(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function with multiple fields set to different values
        search_params = PictureSearch(field1='value1', field2='value2', field3='value3')
        result = self.search_pictures(search_params, sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)
        
        


class Test_Search_Users:

    # Returns a list of UserResponse objects when given valid search parameters.
    def test_valid_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)
    
        # Act
        result = search_users(search_params, db)
    
        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Raises an HTTPException with status code 403 when the current user is not a moderator or administrator.
    def test_non_moderator_or_admin_user(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)
    
        # Act and Assert
        with pytest.raises(HTTPException) as exc:
            search_users(search_params, db)
    
        assert exc.value.status_code == 403

    # Returns an empty list when no users match the search parameters.
    def test_returns_empty_list_when_no_users_match_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    # Returns a list of UserResponse objects when given search parameters that match multiple users.
    def test_returns_list_of_user_responses_when_given_matching_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Returns an empty list when given search parameters that do not match any users.
    def test_empty_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    # Returns a list of UserResponse objects when given search parameters that match a single user.
    def test_returns_list_of_userresponse_objects_when_given_matching_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Returns a list of UserResponse objects when given search parameters that include a match on a user's email address.
    def test_returns_list_of_userresponse_objects_with_matching_email(self):
        # Arrange
        search_params = UserSearch(email="test@example.com")
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Returns a list of UserResponse objects when given search parameters that include a match on a user's username.
    def test_returns_list_of_userresponse_objects_with_matching_username(self):
        # Arrange
        search_params = UserSearch(username="john")
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)
        

class Test_Search_Users_By_Picture:

    # The function is called with valid user_id, picture_id, rating, and added_after parameters.
    def test_valid_parameters(self, mocker):
        # Mock the dependencies
        mocker.patch('src.routes.search.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=1, picture_id=1, rating=5, added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with user_id parameter set to a non-existent user id.
    def test_nonexistent_user_id(self, mocker):
        # Mock the dependencies
        mocker.patch('src.routes.search.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=999, picture_id=1, rating=5, added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with valid added_after parameter.
    def test_valid_added_after_parameter(self, mocker):
        # Mock the dependencies
        mocker.patch('src.database.db.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with valid user_id parameter.
    def test_valid_user_id_parameter(self, mocker):
        # Mock the dependencies
        mocker.patch('src.database.db.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=1)

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The current user is a moderator and the function is called with valid parameters.
    def test_valid_parameters(self, mocker):
        # Mock the dependencies
        mocker.patch('src.routes.search.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=1, picture_id=1, rating=5, added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with valid rating parameter.
    def test_valid_rating_parameter(self, mocker):
        # Mock the dependencies
        mocker.patch('src.database.db.get_db')
        mocker.patch('src.services.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.services.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(rating=5)

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with valid picture_id parameter.
    def test_valid_picture_id_parameter(self, mocker):
        # Mock the dependencies
        mocker.patch('src.database.db.get_db')
        mocker.patch('src.services.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.services.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(picture_id=1)

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The current user is an administrator and the function is called with valid parameters.
    def test_valid_parameters(self, mocker):
        # Mock the dependencies
        mocker.patch('src.routes.search.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=1, picture_id=1, rating=5, added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value