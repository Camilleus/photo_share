from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict
from datetime import datetime

from src.database.models import Picture, Tag, User
from src.database.db import get_db
from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch
from src.services.auth import Auth


get_current_user = Auth.get_current_user


router = APIRouter(tags=["search"])
    
    
class PictureSearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_pictures(self, search_params: PictureSearch, rating: Optional[int] = None, added_after: Optional[datetime] = None, sort_by: Optional[str] = "created_at", sort_order: Optional[str] = "desc") -> List[PictureResponse]:
        query = self.db.query(Picture)

        self._apply_keyword_filter(query, search_params)
        self._apply_tag_filter(query, search_params)
        self._apply_rating_filter(query, rating)
        self._apply_added_after_filter(query, added_after)
        self._apply_sorting(query, sort_by, sort_order)

        pictures = query.all()
        pydantic_pictures = [picture.to_pydantic() for picture in pictures]

        return pydantic_pictures

    def _apply_keyword_filter(self, query, search_params):
        if search_params.keywords:
            query = query.filter(Picture.description.ilike(f"%{search_params.keywords}%"))

    def _apply_tag_filter(self, query, search_params):
        if search_params.tags:
            tag_query = self.db.query(Tag)
            tag_ids = [tag.id for tag in tag_query.filter(Tag.name.in_(search_params.tags)).all()]
            query = query.join(Picture.tags).filter(Tag.id.in_(tag_ids))

    def _apply_rating_filter(self, query, rating):
        if rating is not None:
            query = query.filter(Picture.rating >= rating)

    def _apply_added_after_filter(self, query, added_after):
        if added_after is not None:
            query = query.filter(Picture.created_at >= added_after)

    def _apply_sorting(self, query, sort_by, sort_order):
        if sort_by not in ["rating", "created_at"]:
            sort_by = "created_at"

        if sort_order not in ["asc", "desc"]:
            sort_order = "desc"

        query = query.order_by(getattr(Picture, sort_by).desc() if sort_order == "desc" else getattr(Picture, sort_by))


class UserSearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_users(self, search_params: UserSearch, username: Optional[str] = None, email: Optional[str] = None) -> List[UserResponse]:
        query = self.db.query(User)

        self._apply_keyword_filter(query, search_params)
        self._apply_username_filter(query, username)
        self._apply_email_filter(query, email)

        users = query.all()
        pydantic_users = [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                avatar=user.avatar,
                picture_count=len(user.pictures),
            ) for user in users
        ]

        return pydantic_users

    def _apply_keyword_filter(self, query, search_params):
        if search_params.keywords:
            query = query.filter(
                or_(User.username.ilike(f"%{search_params.keywords}%"), User.email.ilike(f"%{search_params.keywords}%"))
            )

    def _apply_username_filter(self, query, username):
        if username:
            query = query.filter(User.username.ilike(f"%{username}%"))

    def _apply_email_filter(self, query, email):
        if email:
            query = query.filter(User.email.ilike(f"%{email}%"))


class UserPictureSearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_users_by_picture(self, user_id: Optional[int] = None, picture_id: Optional[int] = None, rating: Optional[int] = None, added_after: Optional[datetime] = None) -> List[UserResponse]:
        query = self.db.query(Picture.user_id, func.count(Picture.id).label("picture_count"))

        self._apply_user_id_filter(query, user_id)
        self._apply_picture_id_filter(query, picture_id)
        self._apply_rating_filter(query, rating)
        self._apply_added_after_filter(query, added_after)

        query = query.group_by(Picture.user_id)
        users = query.all()

        pydantic_users = [
            UserResponse(
                id=user.user_id,
                username=user.user.username,
                email=user.user.email,
                avatar=user.user.avatar,
                picture_count=user.picture_count,
            ) for user in users
        ]

        return pydantic_users

    def _apply_user_id_filter(self, query, user_id):
        if user_id is not None:
            query = query.filter(Picture.user_id == user_id)

    def _apply_picture_id_filter(self, query, picture_id):
        if picture_id is not None:
            query = query.filter(Picture.rating >= picture_id)

    def _apply_rating_filter(self, query, rating):
        if rating is not None:
            query = query.filter(Picture.rating >= rating)

    def _apply_added_after_filter(self, query, added_after):
        if added_after is not None:
            query = query.filter(Picture.created_at >= added_after)