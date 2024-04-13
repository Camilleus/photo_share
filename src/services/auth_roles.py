
from fastapi import Depends, HTTPException, status

from src.services.auth import auth_service
from src.database.models import User
from src.repository import pictures as repository_pictures

def is_admin_or_moderator(current_user: User = Depends(auth_service.get_current_user)):
    if not current_user.admin and not current_user.moderator:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to perform this action.")
    return current_user


def is_admin_or_owner(picture_id: int, current_user: User = Depends(auth_service.get_current_user)):
    """
    Check if the current user is an admin or the owner of the picture.
    """
    picture = repository_pictures.get_one_picture(picture_id=picture_id)
    if picture is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")

    if not current_user.admin and current_user.id != picture.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to perform this action.")

    return current_user

def is_admin(current_user: User = Depends(auth_service.get_current_user)):
    """
    Check if the current user is an admin.
    """
    if not current_user.admin:
        raise HTTPException(status_code=403,
                            detail="You are not authorized to perform this action")
    return current_user