from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import PictureDescription
from src.repository import descriptions as repository_descriptions
from src.repository import pictures as repository_pictures
from src.database.models import User
from src.services.auth import auth_service


router = APIRouter(prefix='/descriptions', tags=["descriptions"])


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=PictureDescription)
async def upload_description(
        picture_id: int,
        description: str,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Upload a description for a picture to the database.

    This endpoint uploads a description for a picture identified by picture_id to the database.

    Parameters:
    - picture_id (int): The ID of the picture for which the description is being uploaded.
    - description (str): The description to be associated with the picture.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The description of the uploaded picture as a PictureDescription instance.
    """

    if not current_user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to upload description")

    descriptions = await repository_descriptions.upload_description(picture_id=picture_id, description=description, db=db)
    return descriptions


@router.get("/", response_model=List[PictureDescription])
async def get_all_descriptions(
        skip: int = 0,
        limit: int = 20,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
) -> list[str]:
    """
    Retrieve all picture descriptions from the database.

    This endpoint retrieves all picture descriptions from the database with optional pagination.

    Parameters:
    - skip (int): Number of records to skip for pagination.
    - limit (int): Maximum number of records to retrieve for pagination.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - A list of PictureDescription instances representing the retrieved descriptions.
    """

    if not current_user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to get all descriptions")

    descriptions = await repository_descriptions.get_all_descriptions(skip=skip, limit=limit, db=db)
    return descriptions


@router.get("/{picture_id}", response_model=PictureDescription)
async def get_one_description(
        picture_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Retrieve a specific picture description from the database.

    This endpoint retrieves the description for a picture identified by picture_id from the database.

    Parameters:
    - picture_id (int): The ID of the picture for which the description is being retrieved.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The description of the specified picture as a PictureDescription instance.
    """

    if not current_user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to description")

    description = await repository_descriptions.get_one_description(picture_id=picture_id, db=db)
    if description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return description


@router.put("/{picture_id}", response_model=PictureDescription)
async def update_description(
        picture_id: int,
        new_description: str,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Update the description for a picture in the database.

    This endpoint updates the description for a picture identified by picture_id in the database.

    Parameters:
    - picture_id (int): The ID of the picture for which the description is being updated.
    - new_description (str): The new description to replace the existing one.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The updated description of the specified picture as a PictureDescription instance.
    """

    picture = await repository_pictures.get_one_picture(picture_id=picture_id, db=db)

    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    if not current_user.id == picture.user_id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this description")

    description = await repository_descriptions.update_description(picture_id=picture_id, new_description=new_description, db=db)

    return description


@router.delete("/{picture_id}", response_model=PictureDescription)
async def delete_description(
        picture_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Delete the description for a picture from the database.

    This endpoint deletes the description for a picture identified by picture_id from the database.

    Parameters:
    - picture_id (int): The ID of the picture for which the description is being deleted.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The deleted description of the specified picture as a PictureDescription instance.
    """

    picture = await repository_pictures.get_one_picture(picture_id=picture_id, db=db)

    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    if not current_user.id == picture.user_id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this description")

    description = await repository_descriptions.delete_description(picture_id=picture_id, db=db)

    return description
