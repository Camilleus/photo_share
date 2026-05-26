from typing import Type
from sqlalchemy.orm import Session
from src.database.models import Picture, User
from fastapi import HTTPException


async def upload_picture(picture_url: str,
                         picture_json: dict,
                         user: User,
                         qr: str,
                         db: Session,
                         description: str = None,
                         media_type: str = 'image',
                         picture_secondary_url: str = None,
                         is_bereal: bool = False) -> Picture:

    """
    Asynchronously uploads a picture to the database.

    This function takes a URL, a dictionary containing picture metadata (picture_json),
    a user object, a URL for the QR code of the original picture, and a database session.
    It creates a new Picture object with the provided URL, picture metadata, user ID,
    and QR code URL, adds it to the database, commits the transaction, and refreshes
    the session to retrieve the newly created picture.

    Parameters:
    - picture_url (str): The URL of the picture to upload.
    - picture_json (dict): A dictionary containing metadata of the picture.
    - user (User): The user object associated with the picture.
    - qr (str): The URL for the QR code of the original picture.
    - db (Session): The SQLAlchemy session used to interact with the database.
    - description (str): The description of the picture.
    - media_type (str): The media type of the picture (e.g., 'image', 'video', 'gif', 'reel').
    - picture_secondary_url (str): The URL of the secondary picture for BeReal.
    - is_bereal (bool): Flag indicating if the post is a BeReal post.

    Returns:
    - Picture: The newly uploaded Picture object.
    """
    
    picture = Picture(
        picture_url=picture_url,
        picture_json=picture_json,
        user_id=user.id,
        qr_code_picture=qr,
        description=description,
        media_type=media_type,
        picture_secondary_url=picture_secondary_url,
        is_bereal=is_bereal
    )
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture


async def get_all_pictures(skip: int, limit: int, db: Session) -> list[Type[Picture]]:
    """
    Asynchronously retrieves all pictures from the database.

    This function retrieves all pictures stored in the database, with optional
    support for pagination.

    Parameters:
    - skip (int): The number of pictures to skip.
    - limit (int): The maximum number of pictures to retrieve.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - List[Type[Picture]]: A list of Picture objects representing the retrieved pictures.
    """

    return db.query(Picture).offset(skip).limit(limit).all()


async def get_one_picture(picture_id: int, db: Session) -> Picture:
    """
    Asynchronously retrieves a specific picture from the database.

    This function retrieves a picture with the specified ID from the database.

    Parameters:
    - picture_id (int): The ID of the picture to retrieve.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Picture: The Picture object representing the retrieved picture.
    """

    return db.query(Picture).filter(Picture.id == picture_id).first()


async def update_picture(picture_id: int, url: str, user: User, db: Session, media_type: str = None) -> Picture | None:
    """
    Asynchronously updates a picture in the database.

    This function updates the specified picture in the database with a new URL
    and user ID.

    Parameters:
    - picture_id (int): The ID of the picture to update.
    - url (str): The new URL of the picture.
    - user (User): The user object associated with the picture.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Union[Picture, None]: The updated Picture object if successful, otherwise None.
    """

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        picture.user_id = user.id
        picture.picture_url = url
        if media_type:
            picture.media_type = media_type
        db.commit()
        db.refresh(picture)
    return picture


async def delete_picture(picture_id: int, db: Session) -> Picture | None:
    """
    Asynchronously deletes a picture from the database.

    This function deletes the specified picture from the database.

    Parameters:
    - picture_id (int): The ID of the picture to delete.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Union[Picture, None]: The deleted Picture object if successful, otherwise None.
    """

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        db.delete(picture)
        db.commit()
    return picture


async def upload_edited_picture(picture: dict, picture_edited: dict, picture_edited_url: str, qr: str, db: Session) -> Picture | None:
    """
    Uploads the edited picture to the database and returns the edited URL and QR code.

    Parameters:
    - picture (dict): The original picture object to be updated with the edited URL and QR code.
    - picture_edited (dict): The edited picture object.
    - picture_edited_url (str): The edited URL of the picture.
    - qr (str): The QR code associated with the edited picture.
    - db (Session): An SQLAlchemy database session instance provided by the FastAPI dependency injection system.

    Returns:
    - dict: A dictionary containing the edited URL and QR code.

    Raises:
    - HTTPException: If there is an issue committing the changes to the database.
    """

    picture.picture_edited_url = picture_edited_url
    picture.picture_edited_json = picture_edited
    picture.qr_code_picture_edited = qr
    db.commit()

    return {
        "picture_edited_url": picture_edited_url,
        "qr_code_picture_edited": qr
    }

async def validate_edit_parameters(picture_edit):
    """
    Validate the parameters provided for editing a picture.

    Parameters:
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

    Raises:
    - HTTPException: If any of the parameters are invalid or conflicting.
    """

    try:
        if picture_edit.improve != "0":
            improve_value = int(picture_edit.improve)
            if not 0 <= improve_value <= 100:
                raise ValueError("Value of 'improve' must be between 0 and 100.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.contrast != "0":
            contrast_value = int(picture_edit.contrast)
            if not -100 <= contrast_value <= 100:
                raise ValueError("Value of 'contrast' must be between -100 and 100.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.unsharp_mask != "0":
            unsharp_mask_value = int(picture_edit.unsharp_mask)
            if not 1 <= unsharp_mask_value <= 2000:
                raise ValueError("Value of 'unsharp_mask' must be between 1 and 2000.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.brightness != "0":
            brightness_value = int(picture_edit.brightness)
            if not -99 <= brightness_value <= 100:
                raise ValueError("Value of 'brightness' must be between -99 and 100.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.gamma != "0":
            gamma_value = int(picture_edit.gamma)
            if not -50 <= gamma_value <= 150:
                raise ValueError("Value of 'gamma' must be between -50 and 150.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not isinstance(picture_edit.grayscale, bool):
        raise HTTPException(status_code=400, detail="'grayscale' must be a boolean value.")

    if not isinstance(picture_edit.redeye, bool):
        raise HTTPException(status_code=400, detail="'redeye' must be a boolean value.")
    
    try:
        if picture_edit.gen_replace != "from_null;to_null" and picture_edit.gen_remove != "prompt_null":
            raise HTTPException(status_code=400, detail="You can only specify either gen_replace or gen_remove, not both.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def parse_transform_effects(picture_edit):
    """
    Parse the transformation effects based on the provided parameters for editing a picture.

    Parameters:
    - picture_edit (PictureEdit): An object containing the parameters for editing the picture.

    Returns:
    - list: A list of dictionaries representing the transformation effects to be applied to the picture.
    """

    transformation = [
        {'effect': f"gen_replace:{picture_edit.gen_replace}"} if picture_edit.gen_replace != "from_null;to_null" else None,
        {'effect': f"gen_remove:{picture_edit.gen_remove}"} if picture_edit.gen_remove != "prompt_null" else None,
        {'effect': f"improve:outdoor:{picture_edit.improve}"} if picture_edit.improve != "0" else None,
        {'effect': f"contrast:{picture_edit.contrast}"} if picture_edit.contrast != "0" else None,
        {'effect': f"unsharp_mask:{picture_edit.unsharp_mask}"} if picture_edit.unsharp_mask != "0" else None,
        {'effect': f"brightness:{picture_edit.brightness}"} if picture_edit.brightness != "0" else None,
        {'effect': f"gamma:{picture_edit.gamma}"} if picture_edit.gamma != "0" else None,
        {'effect': f"grayscale"} if picture_edit.grayscale != False else None,
        {'effect': f"redeye"} if picture_edit.redeye != False else None,
    ]

    transformation = [effect for effect in transformation if effect is not None]

    return transformation
