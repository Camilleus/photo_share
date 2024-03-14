from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime

from src.database.db import get_db
from src.schemas import PictureResponse, UserResponse, UserSearch
from src.repository import search as repository_search
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.services.auth import auth_service as Auth


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

@router.post("/users", response_model=List[UserResponse])
async def search_pictures(
        keyword: Optional[str] = "",
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "desc",
        db: Session = Depends(get_db)
    ):

    users = await repository_search.search_users(keyword=keyword, sort_by=sort_by, sort_order=sort_order, db=db)

    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")



@router.post("/users_by_picture", response_model=List[UserResponse])
async def search_users_by_picture(
        keyword: Optional[str] = "",
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "desc",
        db: Session = Depends(get_db)
    ):
    users = await repository_search.search_users_by_picture(keyword=keyword, sort_by=sort_by, sort_order=sort_order, db=db)

    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")

