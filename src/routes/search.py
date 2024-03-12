from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict
from datetime import datetime

from src.database.models import Picture, Tag, User
from src.database.db import get_db
from src.schemas import PictureResponse, UserResponse, PictureSearch, UserSearch
from src.services.auth import Auth
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService

get_current_user = Auth.get_current_user


router = APIRouter(tags=["search"])


def search_pictures(search_params: PictureSearch, sort_by: Optional[str] = "created_at", sort_order: Optional[str] = "desc", db: Session = Depends(get_db)) -> List[PictureResponse]:
    picture_search_service = PictureSearchService(db)
    return picture_search_service.search_pictures(search_params, sort_by, sort_order)

router.get("/search/pictures", response_model=List[PictureResponse])(search_pictures)


def search_users(search_params: UserSearch, db: Session = Depends(get_db)) -> List[UserResponse]:
    user_search_service = UserSearchService(db)
    return user_search_service.search_users(search_params)

router.get("/search/users", response_model=List[UserResponse])(search_users)


def search_users_by_picture(user_id: Optional[int] = None, picture_id: Optional[int] = None, rating: Optional[int] = None, added_after: Optional[datetime] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[UserResponse]:
    if not (current_user.is_moderator or current_user.is_admin):
        raise HTTPException(status_code=403, detail="User filtering is only available to moderators and administrators.")

    user_picture_search_service = UserPictureSearchService(db)
    return user_picture_search_service.search_users_by_picture(user_id, picture_id, rating, added_after)

router.get("/search/users/by_picture", response_model=List[UserResponse])(search_users_by_picture)