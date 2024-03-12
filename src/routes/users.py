from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.repository.users import get_user_by_id, list_all_users, update_user_name, ban_user, get_user_by_username

from src.services.auth import auth_service
from src.schemas import UserDb, UserUpdateName
from src.conf.cloudinary import configure_cloudinary, generate_random_string

router = APIRouter(prefix="/users", tags=["users"])

rate_limit = RateLimiter(times=10, seconds=60)


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)) -> UserDb:
    """
    Read the authenticated user's profile.

    Args:
        current_user (User): The authenticated user.

    Returns:
        UserDb: The user's profile.
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(),
                             current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)) -> UserDb:
    """
    Update the avatar for the authenticated user.

    Args:
        file (UploadFile): Uploaded file containing the new avatar image.
        current_user (User): The authenticated user.
        db (Session): SQLAlchemy database session.

    Returns:
        UserDb: The updated user profile.
    """
    configure_cloudinary()
    random_string = generate_random_string()

    r = cloudinary.uploader.upload(file.file, public_id=f'avatars/{random_string}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'avatars/{random_string}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user


@router.get('/all',
            response_model=List[UserDb],
            dependencies=[Depends(auth_service.require_role(required_role="moderator"))])
async def read_all_users(db: Session = Depends(get_db),
                         ) -> List[UserDb]:
    """
    Asynchronously retrieves all users from the database.

    This endpoint queries the database for all users and returns them as a list of Pydantic models
    conforming to `UserDb`. This operation is non-blocking and is performed asynchronously.

    Args:
        db (Session): The database session dependency injected by FastAPI.

    Returns:
        List[UserDb]: A list of users represented as Pydantic models.
    """
    users = await list_all_users(db=db)
    return users


@router.patch('/update/{user_id}', response_model=UserDb)
async def update_user_name_route(user_id: int,
                                 user_name_update: UserUpdateName,
                                 db: Session = Depends(get_db)
                                 ) -> UserDb:
    """
    Asynchronously updates the name of a specific user identified by their user ID.

    This endpoint allows for updating the username of a specific user. The new username is provided
    in the request body as a JSON object. If the user is found and the username is successfully updated,
    the updated user data is returned as a Pydantic model conforming to `UserDb`.

    Args:
        user_id (int): The unique identifier of the user whose name is to be updated.
        user_name_update (UserUpdateName): The new name to assign to the user, received as request body.
        db (Session): The database session dependency injected by FastAPI.

    Returns:
        UserDb: The updated user data as a Pydantic model.
    """
    updated_user = await update_user_name(user_id=user_id, new_name=user_name_update.username, db=db)
    return updated_user


@router.post("/ban/{user_id}")
async def ban_user_route(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    Ban a specific user identified by their user ID.

    This endpoint bans the user specified by `user_id`. It sets the `ban_status` flag for the user to True,
    effectively banning them from accessing certain features of the application.

    Args:
        user_id (int): The unique identifier of the user to ban.
        db (Session): The SQLAlchemy database session used to execute the ban operation.
        current_user (User): The current authenticated user. Must be an admin.

    Returns:
        str: Confirmation message indicating successful ban.

    Raises:
        HTTPException: A 404 error if no user with the specified ID exists.
                      A 403 error if the current user is not authorized to ban the account.
    """
    try:
        await ban_user(user_id, db, current_user)
        return {"message": "User has been banned successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_account")
async def delete_own_account(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    Delete the authenticated user's own account.

    This endpoint allows the authenticated user to delete their own account.

    Args:
        current_user (User): The authenticated user.
        db (Session): The SQLAlchemy database session used to execute the delete operation.

    Returns:
        dict: A confirmation message indicating successful deletion.
    """
    try:

        db.delete(current_user)
        db.commit()
        
        return {"message": "Your account has been successfully deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/name/{username}", response_model=UserDb)
async def read_user_by_username(username: str, db: Session = Depends(get_db)) -> UserDb:
    """
    Read the user's profile by their unique username.

    Args:
        username (str): The unique username of the user.
        db (Session): SQLAlchemy database session.

    Returns:
        UserDb: The user's profile as a Pydantic model.
    """
    user = await get_user_by_username(db=db, username=username)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.get('/{user_id}', response_model=UserDb)
async def read_user(user_id: int,
                    db: Session = Depends(get_db)
                    ) -> UserDb:
    """
    Asynchronously retrieves a user by their ID from the database.

    This endpoint queries the database for a user with the specified `user_id` and returns the user data
    as a Pydantic model conforming to `UserDb`. If the user is not found, an HTTP 404 error is raised.

    Args:
        user_id (int): The unique identifier of the user to retrieve.
        db (Session): The database session dependency injected by FastAPI.

    Returns:
        UserDb: The requested user's data as a Pydantic model.
    """
    db_user = await get_user_by_id(db=db, user_id=user_id)
    return db_user
