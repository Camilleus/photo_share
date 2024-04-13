from typing import Type, List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel, UserDb
from src.services.auth import auth_service


async def get_user_by_email(email: str, db: Session) -> Type[User]:
    """
    Get a user by their email address.

    Args:
        email (str): Email address of the user.
        db (Session): SQLAlchemy database session.

    Returns:
        Type[User]: The user object or None if not found.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user.

    Args:
        body (UserModel): Data for the new user.
        db (Session): SQLAlchemy database session.

    Returns:
        User: The created user.
    """
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_user_by_id(user_id: int,
                         db: Session
                         ) -> UserDb:

    """
    Asynchronously retrieves a user by their ID from the database.

    This function queries the database for a user with the specified `user_id`. If the user exists,
    it returns a Pydantic model (`UserDb`) representation of the user. If the user does not exist,
    it raises an HTTPException with a 400 status code.

    Args:
        user_id (int): The unique identifier of the user to retrieve.
        db (Session): The database session used to execute the query.

    Returns:
        UserDb: A Pydantic model representing the retrieved user's data.

    Raises:
        HTTPException: A 400 error if the user with the specified ID does not exist.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return UserDb.from_orm(user)


async def list_all_users(db: Session) -> List[User]:
    """
    Asynchronously retrieves a list of all users from the database.

    This function queries the database for all users and returns a list of SQLAlchemy `User` model
    instances representing all users in the database.

    Args:
        db (Session): The database session used to execute the query.

    Returns:
        List[User]: A list of all user instances in the database.

    """
    users = db.query(User).all()
    return users


async def update_user_name(user_id: int,
                           new_name: str,
                           db: Session
                           ) -> UserDb:
    """
    Asynchronously updates the name of a specific user identified by their user ID.

    This function searches for a user with the specified `user_id` and updates their username to
    `new_name`. If the user is found and the name is updated, it returns a Pydantic model (`UserDb`)
    representation of the updated user. If no user is found, it raises an HTTPException with a 404 status code.

    Args:
        user_id (int): The unique identifier of the user whose name is to be updated.
        new_name (str): The new name to assign to the user.
        db (Session): The database session used to execute the update operation.

    Returns:
        UserDb: A Pydantic model representing the updated user's data.

    Raises:
        HTTPException: A 404 error if no user with the specified ID exists.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = new_name
    db.commit()
    db.refresh(user)
    return UserDb.from_orm(user)


async def ban_user(user_id: int, db: Session, current_user: User) -> None:
    """
    Ban a specific user identified by their user ID.

    This function searches for a user with the specified `user_id` and sets their `ban_status` flag to True.
    If no user is found with the specified ID, it raises an HTTPException with a 404 status code.
    If the current user is not an admin, it raises an HTTPException with a 403 status code.

    Args:
        user_id (int): The unique identifier of the user to ban.
        db (Session): The database session used to execute the ban operation.
        current_user (User): The current authenticated user.

    Returns:
        None: Indicates successful ban.

    Raises:
        HTTPException: A 404 error if no user with the specified ID exists.
                      A 403 error if the current user is not authorized to ban the account.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not current_user.admin:
        raise HTTPException(status_code=403, detail="You are not authorized to ban accounts.")

    user.ban_status = True
    db.commit()


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a user.

    Args:
        user (User): The user for whom to update the token.
        token (str | None): The new refresh token or None to clear the existing token.
        db (Session): SQLAlchemy database session.
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm the email address for a user.

    Args:
        email (str): Email address to confirm.
        db (Session): SQLAlchemy database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the avatar for a user.

    Args:
        email (str): Email address of the user.
        url (str): New avatar URL.
        db (Session): SQLAlchemy database session.

    Returns:
        User: The updated user object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def upgrade_password(user: UserModel, new_password: str, db: Session):
    """
    Upgrade the password for a user.

    Args:
        user (UserModel): The user for whom to upgrade the password.
        new_password (str): The new password.
        db (Session): SQLAlchemy database session.
    """
    user.password = auth_service.get_password_hash(new_password)
    db.commit()


async def get_user_by_username(username: str, db: Session):
    """
    Asynchronously retrieves a user by their username from the database.

    This function queries the database for a user with the specified `username`. If the user exists,
    it returns a Pydantic model (`UserDb`) representation of the user. If the user does not exist,
    it raises an HTTPException with a 400 status code.

    Args:
        username (str): The unique username of the user to retrieve.
        db (Session): The database session used to execute the query.

    Returns:
        UserDb: A Pydantic model representing the retrieved user's data.

    Raises:
+        HTTPException: A 404 error if the user with the specified username does not exist.
-        HTTPException: A 400 error if the user with the specified username does not exist.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDb.from_orm(user)
