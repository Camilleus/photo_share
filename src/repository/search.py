from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from typing import List, Optional
from sqlalchemy import or_

from src.database.models import Picture, User, Tag, PictureTagsAssociation
from src.database.db import get_db
from src.schemas import PictureResponse, UserResponse


async def search_pictures(keyword: Optional[str] = "",
                          sort_by: Optional[str] = "created_at",
                          sort_order: Optional[str] = "desc",
                          db: Session = Depends(get_db)
                          ) -> List[PictureResponse]:

    if sort_by not in ["rating", "created_at"]:
        sort_by = "created_at"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    tags_ids = [tag.id for tag in db.query(Tag).filter(Tag.name.like(f"%{keyword}%")).all()]

    pictures_ids = [pic_id for (pic_id,) in db.query(PictureTagsAssociation.picture_id).filter(
        PictureTagsAssociation.tag_id.in_(tags_ids)).all()]

    pictures = db.query(Picture).filter(
        or_(
            Picture.description.like(f"%{keyword}%"),
            Picture.id.in_(pictures_ids)
        )
    ).all()

    if not pictures:
        raise HTTPException(status_code=404, detail="Picture not found")

    pictures = sorted(pictures, key=lambda x: getattr(x, sort_by), reverse=(sort_order == "desc"))

    picture_responses = []
    for picture in pictures:
        tag_ids = [tag.id for tag in picture.tags]
        picture_response = PictureResponse(
            id=picture.id,
            description=picture.description,
            picture_url=picture.picture_url,
            average_rating=picture.average_rating,
            created_at=picture.created_at,
            user_id=picture.user_id,
            tags=tag_ids,
            qr_code_picture=picture.qr_code_picture
        )
        picture_responses.append(picture_response)

    return picture_responses




async def search_users(keyword: Optional[str] = "",
                       sort_by: Optional[str] = "created_at",
                       sort_order: Optional[str] = "desc",
                       db: Session = Depends(get_db)
                       ) -> List[UserResponse]:

    if sort_by not in ["rating", "created_at"]:
        sort_by = "created_at"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    users_ids = [id for (id) in db.query(User.id).filter(
        User.id.in_(users_ids)).all()]
    
    users = db.query(User).filter(
        or_(
            User.username.like(f"%{keyword}%"),
            User.email.like(f"%{keyword}%"),
            User.id.in_(users_ids)
        )
    ).all()

    if not users:
        raise HTTPException(status_code=404, detail="Users not found")

    users = sorted(users, key=lambda x: getattr(x, sort_by), reverse=(sort_order == "desc"))

    user_responses = []
    for user in users:
        user_response = UserResponse(
            id=user.id,
            created_at=user.created_at,
            email=user.email,
            username=user.username
        )
        user_responses.append(user_response)

    return user_responses




async def search_users_by_picture(keyword: Optional[str] = "",
                       sort_by: Optional[str] = "created_at",
                       sort_order: Optional[str] = "desc",
                       db: Session = Depends(get_db)
                       ) -> List[UserResponse]:

    if sort_by not in ["rating", "created_at"]:
        sort_by = "created_at"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    users_ids = [id for (id) in db.query(User.id).filter(
        User.id.in_(users_ids)).all()]

    users = db.query(User).filter(
        or_(
            User.username.like(f"%{keyword}%"),
            User.email.like(f"%{keyword}%"),
            User.id.in_(users_ids)
        )
    ).all()

    if not users:
        raise HTTPException(status_code=404, detail="Users not found")

    users = sorted(users, key=lambda x: getattr(x, sort_by), reverse=(sort_order == "desc"))

    user_responses = []
    for user in users:
        user_response = UserResponse(
            id=user.id,
            created_at=user.created_at,
            email=user.email,
            username=user.username
            pictures=user.pictures
            )
        user_responses.append(user_response)

    return user_responses