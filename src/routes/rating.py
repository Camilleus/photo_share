from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository.rating import add_rating_to_picture, remove_rating_from_picture, get_rating, get_average_of_rating
from src.schemas import Rating, RatingPicture
from src.services.auth import auth_service
from src.services.auth_roles import is_admin

router = APIRouter(prefix="/rating", tags=["rating"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rating(
        data: Rating,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Creates a new rating for a picture.

    - **picture_id**: The identifier of the picture to be rated.
    - **rating**: The rating assigned to the picture, must be one of the allowed values (1-5).
    """

    return await add_rating_to_picture(data.picture_id, data.rating, current_user, db)


@router.delete("/{rating}")
async def delete_rating(
        picture_id: int,
        user_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)):
    """
    Removes a user's rating for a picture.

    - **picture_id**: The identifier of the picture from which the rating is to be removed.
    - **user_id**: The identifier of the user whose rating is to be removed (only accessible by admin).
    """
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to delete rating")
    is_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    result = await remove_rating_from_picture(picture_id, user_id, db)
    return result

@router.post("/picture")
async def get_ratings(
        data: RatingPicture,
        db: Session = Depends(get_db)
):
    """
    Retrieves ratings for a picture.

    - **picture_id**: The identifier of the picture whose ratings are to be retrieved.
    """
    ratings = await get_rating(data.picture_id, db)
    return ratings

@router.post("/average/picture")
async def get_average_rating(
        data: RatingPicture,
        db: Session = Depends(get_db)
):
    """
    Calculates the average rating for a picture.

    - **picture_id**: The identifier of the picture for which the average rating is to be calculated.
    """
    average = await get_average_of_rating(data.picture_id, db)
    return average