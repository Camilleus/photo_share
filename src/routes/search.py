from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict
from datetime import datetime

from src.database.models import Picture, Tag, User
from src.database.db import get_db
from src.schemas import PictureResponse, PictureSearch, UserResponse


from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pickle
from src.repository import users as repository_users


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    

router = APIRouter()

async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Dict:
        """
        Get the current user from the token.

        Args:
            token (str): The access token.
            db (Session): SQLAlchemy database session.

        Returns:
            Dict: The user data.

        Raises:
            HTTPException: If validation fails or user is not found.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user
    
    
@router.post("/search", response_model=List[PictureResponse])
async def search_pictures(
    search_params: PictureSearch,
    rating: Optional[int] = None,
    added_after: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    Search for pictures based on the given keywords or tags, with optional filters for rating and added date.

    Args:
        search_params (PictureSearch): The search parameters, which include keywords and/or tags.
        rating (Optional[int], optional): The minimum rating for the pictures. Defaults to None.
        added_after (Optional[datetime], optional): The earliest added date for the pictures. Defaults to None.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[PictureResponse]: A list of pictures matching the search criteria.
    """
    query = db.query(Picture)

    if search_params.keywords:
        query = query.filter(Picture.description.ilike(f"%{search_params.keywords}%"))

    if search_params.tags:
        tag_query = db.query(Tag)
        tag_ids = [tag.id for tag in tag_query.filter(Tag.name.in_(search_params.tags)).all()]
        query = query.join(Picture.tags).filter(Tag.id.in_(tag_ids))

    if rating is not None:
        query = query.filter(Picture.rating >= rating)

    if added_after is not None:
        query = query.filter(Picture.created_at >= added_after)

    pictures = query.all()

    pydantic_pictures = [picture.to_pydantic() for picture in pictures]

    return pydantic_pictures


@router.post("/search/user", response_model=List[UserResponse])
async def search_users_by_pictures(
    user_id: Optional[int] = None,
    picture_id: Optional[int] = None,
    rating: Optional[int] = None,
    added_after: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search for users based on the pictures they have added, with optional filters for rating and added date.

    Args:
        user_id (int): The ID of the user who uploaded the pictures.
        rating (Optional[int], optional): The minimum rating for the pictures. Defaults to None.
        added_after (Optional[datetime], optional): The earliest added date for the pictures. Defaults to None.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(get_current_active_user).

    Returns:
        List[UserResponse]: A list of users matching the search criteria.

    Raises:
        HTTPException: If the user is not a moderator or an administrator.
    """
    if not (current_user.is_moderator or current_user.is_admin):
        raise HTTPException(status_code=403, detail="User filtering is only available to moderators and administrators.")

    query = db.query(Picture.user_id, func.count(Picture.id).label("picture_count"))

    if user_id is not None:
        query = query.filter(Picture.user_id == user_id)

    if picture_id is not None:
        query = query.filter(Picture.rating >= picture_id)
        
    if rating is not None:
        query = query.filter(Picture.rating >= rating)
        
    if added_after is not None:
        query = query.filter(Picture.created_at >= added_after)

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