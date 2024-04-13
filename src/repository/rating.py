from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Rating, User


async def add_rating_to_picture(picture_id: int, rating: int, user: User, db: Session):
    """
    Adds or updates a rating for a picture by a specific user.

    Parameters:
        picture_id (int): The ID of the picture to rate.
        rating (int): The rating value.
        user (User): The user giving the rating.
        db (Session): Database session object.

    Returns:
        dict: A message indicating that the rating was successfully created or updated.
    """
    rating_record = db.query(Rating).filter(and_(Rating.picture_id == picture_id, Rating.user_id == user.id)).first()
    if rating_record:
        rating_record.rat = rating
    else:
        new_rating = Rating(picture_id=picture_id, rat=rating, user_id=user.id)
        db.add(new_rating)
    db.commit()
    return {"message": "The rating was successfully created or updated."}


async def remove_rating_from_picture(picture_id: int, user: User, db: Session):
    """
        Removes a rating from a picture by a specific user.

        Parameters:
            picture_id (int): The ID of the picture from which to remove the rating.
            user (User): The user whose rating is to be removed.
            db (Session): Database session object.

        Returns:
            dict: A message indicating the outcome of the operation.
        """
    rating_record = db.query(Rating).filter(and_(Rating.picture_id == picture_id, Rating.user_id == user.id)).first()
    if rating_record:
        db.delete(rating_record)
        db.commit()
        return {"message": "Rating removed successfully."}
    else:
        return {"message": "No rating found for this user and picture."}

async def remove_rating_from_picture_admin(picture_id: int, user_id: int, db: Session):
    """
        Removes a rating from a picture by a specific user.

        Parameters:
            picture_id (int): The ID of the picture from which to remove the rating.
            user_id (User): The user whose rating is to be removed.
            db (Session): Database session object.

        Returns:
            dict: A message indicating the outcome of the operation.
        """
    rating_record = db.query(Rating).filter(and_(Rating.picture_id == picture_id, Rating.user_id == user_id)).first()
    if rating_record:
        db.delete(rating_record)
        db.commit()
        return {"message": "Rating removed successfully."}
    else:
        return {"message": "No rating found for this user and picture."}


async def get_rating(picture_id: int, db: Session):
    """
    Retrieves all ratings for a specific picture.

    Parameters:
        picture_id (int): The ID of the picture whose ratings are to be retrieved.
        db (Session): Database session object.

    Returns:
        dict: A dictionary containing usernames as keys and their respective ratings as values.
    """
    ratings = db.query(Rating).filter(Rating.picture_id == picture_id).all()
    ratings_dict = {rating.user_id: rating.rat for rating in ratings}
    return ratings_dict


async def get_average_of_rating(picture_id: int, db: Session):
    """
    Calculates the average rating for a specific picture.

    Parameters:
        picture_id (int): The ID of the picture whose average rating is to be calculated.
        db (Session): Database session object.

    Returns:
        dict: A message containing the average rating if available, otherwise indicating no ratings.
    """
    ratings = db.query(Rating).filter(Rating.picture_id == picture_id).all()
    if ratings:
        average = sum(rating.rat for rating in ratings) / len(ratings)
        return {"average_rating": average}
    else:
        return {"message": "No ratings available for this picture."}