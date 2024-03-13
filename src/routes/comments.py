from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from src.services.auth_roles import is_admin_or_moderator
from src.database.db import get_db
from src.database.models import User
from src.schemas import CommentModel, CommentResponse
from src.repository import comments as repository_comments
from src.services.auth import auth_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/{comment_id}", response_model=CommentResponse)
async def read_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The read_comment function will return a comment object with the given id.
    Parameters:
        comment_id (int): Specify the comment id that we want to read
        db (Session): The SQLAlchemy session used to interact with the database.
        current_user (User): Get the current user
    Returns:
        The comment object that matches the given id
    """
    comment = await repository_comments.get_comment(comment_id, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.get("/", response_model=List[CommentResponse])
async def read_comments(
        picture_id: int,
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
):
    """
    The read_comments function will return a list of comments for the picture with the given id.
    Parameters:
    picture_id (int): Get the comments for a specific picture
    skip (int): Skip a number of comments
    limit (int): Limit the number of comments that are returned
    db (Session): The SQLAlchemy session used to interact with the database.
    Returns:
    A list of comments for a given picture_id
    """
    comment = await repository_comments.get_comments(picture_id, skip, limit, db)
    return comment


@router.post("/", response_model=CommentModel,
             status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CommentModel,
        picture_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The create_comment function creates a new comment for the picture with the given id.
        The function takes in a CommentModel object, which contains all the information needed to create
        a new comment. The function introduces a limitation of creating a new comment once every 5 seconds.
    Parameters:
        body (CommentModel): Get the body of the comment
        picture_id (int): Take the picture id for which the comment is created
        db (Session): Access the database
        current_user (User): The User who created this comment.
    Returns:
        A new comment object.
    """
    return await repository_comments.create_comment(body, picture_id, current_user, db)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
        comment_id: int,
        body: CommentModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The update_comment function updates a comment in the database. If comment doesn't exist in database function returns
    "Comment not found".
    Parameters:
        comment_id (int): the id of the comment to be updated.
        body (CommentModel): an object containing all fields that can be updated for a given comment.
        db (Session): The SQLAlchemy session used to interact with the database.
        current_user (User): Get the current user
    Returns:
        The updated comment.
    """
    comment = await repository_comments.update_comment(comment_id, body, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/{contact_id}")
async def remove_contact(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(is_admin_or_moderator)
):
    """
    The remove_comment function is used to delete a comment from the database. The function returns a JSONResponse
    object with status code 200 if successful, or 403 if not.
    Parameters:
        comment_id (int): Get the comment id.
        db (Session): Pass the database session to the function.
        current_user (User): Get the current user.
    Returns:
        The message the comment deleted successfully or not.
    """
    comment = await repository_comments.remove_comment(comment_id, current_user, db)
    if comment is None:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "You can't delete the comment."})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "The comment deleted successfully"})

    
