from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import AdminUserUpdateModel


async def update_user_admin(user_id: int, body: AdminUserUpdateModel, db: Session):
    """
    Updates user details in the database as an admin. This function allows for partial updates,
    meaning only the fields provided in the request body will be updated. It is designed to be used
    by administrators for managing user accounts.

    Parameters:
    - `user_id` (int): The ID of the user to be updated. This identifies the specific user account
                       in the database.
    - `body` (AdminUserUpdateModel): An instance of `AdminUserUpdateModel` containing the updated
                                     values for the user. This model includes fields that can be updated,
                                     and it uses Pydantic's `exclude_unset` feature to ignore fields that
                                     are not included in the request, allowing for partial updates.
    - `db` (Session): The database session, used to execute database operations.

    Returns:
    - The updated user object, reflecting the changes made. If the update is successful, this object
      includes all user fields, both updated and unchanged.

    Raises:
    - HTTPException (404): If no user with the given `user_id` exists in the database, an exception
                            is raised with the detail "User not found".

    The function first retrieves the user by `user_id`. If the user exists, it then proceeds to update
    the user's details based on the provided `body` parameter. Fields not specified in the request body
    are left unchanged. After updating the user details, the function commits the changes to the database
    and refreshes the user object to reflect the updated state.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data_dict = body.dict(exclude_unset=True)
    for key, value in update_data_dict.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user
