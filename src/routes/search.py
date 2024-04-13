from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import List, Optional

from src.database.db import get_db
from src.schemas import PictureResponse, Picturesearch
from src.repository import search as repository_search


router = APIRouter(prefix="/search",tags=["search"])
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import List, Optional

from src.database.db import get_db
from src.schemas import PictureResponse
from src.repository import search as repository_search


router = APIRouter(prefix="/search", tags=["search"])


@router.post("/pictures", response_model=List[PictureResponse])
async def search_pictures(
        keyword: Optional[str] = None,
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "desc",
        db: Session = Depends(get_db)
):
    """
    Searches for images matching the provided keyword and returns a list of image responses.
    The search considers both image descriptions and tags assigned to images.
    Results can be sorted by rating or creation date, in ascending or descending order.

    Args:
        keyword (Optional[str]): The keyword used to filter images. Defaults to `None`.
        sort_by (Optional[str]): The field by which results should be sorted. Possible values are "rating" or "created_at". Defaults to "created_at".
        sort_order (Optional[str]): Specifies whether results should be sorted in ascending ("asc") or descending ("desc") order. Defaults to "desc".
        db (Session): Database session, a dependency injected by FastAPI.

    Returns:
        List[PictureResponse]: A list of PictureResponse objects representing images that meet the search criteria.
    """
    pictures = await repository_search.search_pictures(keyword=keyword, sort_by=sort_by, sort_order=sort_order, db=db)

    return pictures


# def search_pictures(search_params: PictureSearch, sort_by: Optional[str] = "created_at", sort_order: Optional[str] = "desc", db: Session = Depends(get_db)) -> List[PictureResponse]:
#     """
#     A function that searches for pictures based on the provided search parameters and returns a list of PictureResponse objects.
    
#     Args:
#         search_params (PictureSearch): The search parameters used to filter the pictures.
#         sort_by (Optional[str]): The field to sort the pictures by (default is "created_at").
#         sort_order (Optional[str]): The order in which the pictures are sorted (default is "desc").
#         db (Session): The database session used for the operation.
        
#     Returns:
#         List[PictureResponse]: A list of PictureResponse objects that match the search criteria.
#     """
#     picture_search_service = PictureSearchService(db)
#     return picture_search_service.search_pictures(search_params, sort_by, sort_order)

# router.get("/pictures", response_model=List[PictureResponse])(search_pictures)

#     Returns:
#         List[PictureResponse]: A list of PictureResponse objects representing images that meet the search criteria.
#     """
#     pictures = await repository_search.search_pictures(keyword=keyword, sort_by=sort_by, sort_order=sort_order, db=db)

def search_users(search_params: UserSearch, db: Session = Depends(get_db)) -> List[UserResponse]:
    """
    Perform a search for users based on the provided search parameters and return a list of UserResponse objects.
    
    Parameters:
    - search_params: UserSearch object containing the parameters for the user search
    - db: Optional Session object obtained from the get_db dependency
    
    Returns:
    - List of UserResponse objects resulting from the user search
    """
    user_search_service = UserSearchService(db)
    return user_search_service.search_users(search_params)

router.get("/users", response_model=List[UserResponse])(search_users)


def search_users_by_picture(user_id: Optional[int] = None, picture_id: Optional[int] = None, rating: Optional[int] = None, added_after: Optional[datetime] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[UserResponse]:
    """
    A function that searches for users by picture, with optional parameters for user ID, picture ID, rating, and added date. It requires a database session and the current user as dependencies. Returns a list of UserResponse objects.
    """
    if not (current_user.is_moderator or current_user.is_admin):
        raise HTTPException(status_code=403, detail="User filtering is only available to moderators and administrators.")

    user_picture_search_service = UserPictureSearchService(db)
    return user_picture_search_service.search_users_by_picture(user_id, picture_id, rating, added_after)

router.get("/user/_by_picture", tags=["users"], response_model=List[UserResponse])(search_users_by_picture)
