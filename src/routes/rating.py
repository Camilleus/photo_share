from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository.rating import add_rating_to_picture, remove_rating_from_picture, get_rating, get_average_of_rating, \
    remove_rating_from_picture_admin
from src.schemas import Rating, RatingPicture
from src.services.auth import auth_service
from src.services.auth_roles import is_admin, is_admin_or_moderator

router = APIRouter(prefix="/rating", tags=["rating"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rating(
        data: Rating,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Creates a new rating for a specific picture by the current user. This endpoint requires
    authentication and uses the current user's information to associate the rating with the user.

    Parameters:
    - `data`: An instance of `Rating` containing the `picture_id` and the `rating`.
    - `current_user`: The current authenticated user (automatically determined).
    - `db`: The database session.

    Returns:
    - A response indicating the success of the rating creation process, including any relevant
      information about the created rating.
    """

    return await add_rating_to_picture(data.picture_id, data.rating, current_user, db)


@router.delete("/{picture_id}")
async def delete_rating(
        picture_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Removes a rating for a specific picture made by the current user. This endpoint requires
    authentication and uses the current user's information to find and delete the rating.

    Parameters:
    - `picture_id`: The identifier of the picture from which the rating is to be removed.
    - `current_user`: The current authenticated user (automatically determined).
    - `db`: The database session.

    Returns:
    - A response indicating the success of the rating deletion, or a message indicating that
      no rating was found to be deleted.
    """
    result = await remove_rating_from_picture(picture_id, current_user, db)
    return result


@router.delete("/admin/")
async def delete_admin_rating(
        picture_id: int,
        user_id: int,
        current_user: User = Depends(is_admin_or_moderator),
        db: Session = Depends(get_db)):
    """
    Removes a user's rating for a picture.

    - **picture_id**: The identifier of the picture from which the rating is to be removed.
    - **user_id**: The identifier of the user whose rating is to be removed (only accessible by admin).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = await remove_rating_from_picture_admin(picture_id, user_id, db)
    return result


@router.post("/picture")
async def get_ratings(
        data: RatingPicture,
        db: Session = Depends(get_db)
):
    """
    Retrieves all ratings associated with a specific picture. This endpoint is open and does not
    require authentication.

    Parameters:
    - `data`: An instance of `RatingPicture` containing the `picture_id`.
    - `db`: The database session.

    Returns:
    - A list of ratings for the specified picture, including details such as the rating value
      and the user who made the rating.
    """
    ratings = await get_rating(data.picture_id, db)
    return ratings


@router.post("/average/picture")
async def get_average_rating(
        data: RatingPicture,
        db: Session = Depends(get_db)
):
    """
    Calculates and returns the average rating for a specific picture. This endpoint is open and
    does not require authentication.

    Parameters:
    - `data`: An instance of `RatingPicture` containing the `picture_id`.
    - `db`: The database session.

    Returns:
    - The average rating value for the specified picture, calculated from all the ratings
      it has received.
    """
    average = await get_average_of_rating(data.picture_id, db)
    return average