from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional

from src.database.db import get_db
from src.schemas import PictureResponse, UserResponse, UserSearch
from src.repository import search as repository_search
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService


router = APIRouter(prefix="/search", tags=["search"])


@router.post("/pictures", response_model=List[PictureResponse])
async def search_pictures(
        keyword: Optional[str] = "",
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "desc",
        db: Session = Depends(get_db)
):

    pictures = await repository_search.search_pictures(keyword=keyword, sort_by=sort_by, sort_order=sort_order, db=db)

    if pictures is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pictures not found")

@router.get("/users", response_model=List[UserResponse])
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



@router.get("/user/_by_picture", tags=["users"], response_model=List[UserResponse])
def search_users_by_picture(user_id: Optional[int] = None, picture_id: Optional[int] = None, rating: Optional[int] = None, added_after: Optional[datetime] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[UserResponse]:
    """
    A function that searches for users by picture, with optional parameters for user ID, picture ID, rating, and added date. It requires a database session and the current user as dependencies. Returns a list of UserResponse objects.
    """
    if not (current_user.is_moderator or current_user.is_admin):
        raise HTTPException(status_code=403, detail="User filtering is only available to moderators and administrators.")

    user_picture_search_service = UserPictureSearchService(db)
    return user_picture_search_service.search_users_by_picture(user_id, picture_id, rating, added_after)

