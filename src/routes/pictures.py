from typing import List, Type
from fastapi import APIRouter, Depends, HTTPException,  UploadFile, File, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User, Picture
from src.schemas import PictureDB, PictureEdit, PictureResponse
from src.repository import pictures as repository_pictures
from src.services.auth import auth_service
from src.services.qr import generate_qr_and_upload_to_cloudinary
from src.conf.cloudinary import configure_cloudinary, generate_random_string


router = APIRouter(prefix='/pictures', tags=["pictures"])


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=PictureResponse)
async def upload_picture(
        picture: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
) -> PictureDB:
    """
    Upload a picture to the database.

    This endpoint uploads a picture file to the cloud storage using Cloudinary. It then associates
    the uploaded picture with the current user and saves the picture data to the database.

    Parameters:
    - picture (UploadFile): The picture file to be uploaded.
    - current_user (User): The current user authenticated via the authentication service.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The URL of the uploaded picture as a PictureDB instance.
    """
    if not current_user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to upload picture")

    configure_cloudinary()
    picture_name = generate_random_string()
    picture = cloudinary.uploader.upload(picture.file, public_id=picture_name, folder='picture', overwrite=True)
    version = picture.get('version')

    picture_url = cloudinary.CloudinaryImage(picture['public_id']).build_url(version=version)
    qr = await generate_qr_and_upload_to_cloudinary(picture_url, picture)

    picture_in_db = await repository_pictures.upload_picture(picture_url=picture_url, picture_json=picture, user=current_user, qr=qr, db=db)

    return picture_in_db


@router.get("/", response_model=List[PictureResponse])
async def get_all_pictures(
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
) -> list[Type[Picture]]:
    """
    Retrieve all pictures from the database.

    This endpoint retrieves all pictures stored in the database, with optional pagination support.

    Parameters:
    - skip (int): The number of pictures to skip.
    - limit (int): The maximum number of pictures to retrieve.
    - current_user (User): The current user authenticated via the authentication service.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - A list of PictureDB instances representing the retrieved pictures.
    """
    pictures = await repository_pictures.get_all_pictures(skip=skip, limit=limit, db=db)

    return pictures


@router.get("/{picture_id}", response_model=PictureResponse)
async def get_one_picture(
        picture_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
) -> PictureResponse:
    """
    Retrieve a specific picture from the database.

    This endpoint retrieves a picture with the specified ID from the database.

    Parameters:
    - picture_id (int): The ID of the picture to retrieve.
    - current_user (User): The current user authenticated via the authentication service.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The PictureDB instance representing the retrieved picture.
    """

    if not current_user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access to picture")

    picture = await repository_pictures.get_one_picture(picture_id=picture_id, db=db)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    return picture


@router.put("/{picture_id}", response_model=PictureResponse)
async def update_picture(
        picture_id: int,
        picture: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
) -> PictureDB:
    """
    Update a picture in the database.

    This endpoint updates the specified picture in the database with a new picture file.

    Parameters:
    - picture_id (int): The ID of the picture to update.
    - picture (UploadFile): The new picture file to upload.
    - current_user (User): The current user authenticated via the authentication service.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The URL of the updated picture as a PictureDB instance.
    """

    configure_cloudinary()

    random_string = generate_random_string()

    picture_data = await repository_pictures.get_one_picture(picture_id, db)

    if not picture_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    if not current_user.id == picture_data.user_id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this picture")

    picture_uploaded = cloudinary.uploader.upload(picture.file, public_id=f'picture/{current_user.email}', overwrite=True)
    url = cloudinary.CloudinaryImage(f'picture/{random_string}').build_url(version=picture_uploaded.get('version'))

    picture_url = await repository_pictures.update_picture(picture_id=picture_id, url=url, user=current_user, db=db)

    return picture_url


@router.delete("/{picture_id}", response_model=PictureResponse)
async def delete_picture(
        picture_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
) -> PictureDB:
    """
    Delete a picture from the database.

    This endpoint deletes the specified picture from the database.

    Parameters:
    - picture_id (int): The ID of the picture to delete.
    - current_user (User): The current user authenticated via the authentication service.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The PictureDB instance representing the deleted picture.
    """

    picture = await repository_pictures.get_one_picture(picture_id=picture_id, db=db)

    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    if not current_user.id == picture.user_id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this picture")

    deleted_picture = await repository_pictures.delete_picture(picture_id=picture_id, db=db)

    return deleted_picture


@router.post("/edit/{id}", status_code=status.HTTP_201_CREATED)
async def edit_picture(
        picture_id: int,
        picture_edit: PictureEdit,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Edit a picture based on the specified parameters.

    Parameters:
    - picture_id (int): The ID of the picture to be edited.
    - picture_edit (PictureEdit): An object containing the parameters for editing the picture. The parameters include:
        - improve (str): A string representing the improvement level. Must be between 0 and 100.
        - contrast (str): A string representing the contrast level. Must be between -100 and 100.
        - unsharp_mask (str): A string representing the unsharp mask value. Must be between 1 and 2000.
        - brightness (str): A string representing the brightness value. Must be between -99 and 100.
        - gamma (str): A string representing the gamma correction value. Must be between -50 and 150.
        - grayscale (bool): A boolean indicating whether to apply grayscale effect. If True, the effect is applied.
        - redeye (bool): A boolean indicating whether to apply red-eye effect. If True, the effect is applied.
        - gen_replace (str): A string representing the replacement transformation. If specified, 'gen_remove' should not be provided.
        - gen_remove (str): A string representing the removal transformation. If specified, 'gen_replace' should not be provided.
    - current_user (User): The current user authenticated via the authentication service.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency injection system.

    Returns:
    - The edited URL of the picture as a string.

    Raises:
    - HTTPException: If an error occurs during the editing process, such as validation failure or database access issues.
    """

    picture_db = await repository_pictures.get_one_picture(picture_id, db)

    if picture_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    if not current_user.id == picture_db.user_id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to update this picture")

    configure_cloudinary()

    await repository_pictures.validate_edit_parameters(picture_edit)
    picture = picture_db.picture_json
    picture_public_id = picture['public_id']
    picture_version = picture['version']

    transformation = await repository_pictures.parse_transform_effects(picture_edit)
    transformation_url = cloudinary.utils.cloudinary_url(picture_public_id, transformation=transformation)[0]

    picture_edited = cloudinary.uploader.upload(transformation_url, version=picture_version, public_id=f'{picture_public_id}_edited', overwrite=True)
    picture_edited_url = cloudinary.CloudinaryImage(picture_edited['public_id']).build_url(version=picture_version)

    qr = await generate_qr_and_upload_to_cloudinary(picture_edited_url, picture_edited, picture_version)

    return await repository_pictures.upload_edited_picture(picture=picture_db, picture_edited=picture_edited, picture_edited_url=picture_edited_url, qr=qr, db=db)

