from datetime import datetime
from typing import Type, Union

from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Comment, User
from src.schemas import CommentModel


async def create_comment(body: CommentModel, picture_id: int, user: User, db: Session) -> Comment:
    """
    The create_comment function creates a new comment in the database.
    Parameters:
        body (CommentModel): The CommentModel object containing the data to be added to the database.
        picture_id (int): The id of picture that is being commented on.
        user (User): The User who created this comment.
        db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
        A new comment object.
    """
    comment = Comment(user_id=user.id,
                      picture_id=picture_id,
                      content=body.content,
                      created_at=datetime.now()
                      )

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def get_comment(comment_id: int, user: User, db: Session) -> Type[Comment]:
    """
    The get_comment function takes in a comment_id and user object, and returns the Comment object with that id.
    Parameters:
        comment_id (int): The id of the desired Comment.
        user (User): The User who owns the desired Comment.
        db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
        The comment with the given id.
    """
    return db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()


async def get_comments(picture_id: int, skip: int, limit: int, db: Session) -> list[Type[Comment]]:
    """
    The get_comments function takes in a picture_id, skip, limit and db.
    It returns all comments associated with the given picture_id.
    Parameters:
        picture_id (int): Filter the comments by picture_id
        skip (int): Skip a number of comments
        limit (int): Limit the number of comments that are returned
        db (Session): Pass the database session to the function
    Returns:
        A list of comment objects
    """
    return db.query(Comment).filter(Comment.picture_id == picture_id).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()


async def update_comment(comment_id: int, body: CommentModel, user: User, db: Session) -> Comment | None:
    """
    The update_comment function updates a comment in the database.
    Parameters:
        comment_id (int): The id of the comment to update.
        body (CommentModel): The updated content for the Comment object.
        user (User): Check if the user is the owner of the comment
        db (Session): The SQLAlchemy session used to interact with the database.
    Returns:
        The updated comment
    """
    comment = db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()
    if comment:
        comment.content = body.content
        db.commit()
    return comment


async def remove_comment(comment_id: int, user: User, db: Session) -> Union[dict, None]:
    """
    The remove_comment function takes in a comment_id, user and db.
    If the user is an admin or moderator, it will delete the comment from the database.
    Parameters:
        comment_id (int): Specify the id of the comment to be deleted
        user (User): Check if the user is an admin or moderator
        db (Session): The SQLAlchemy session used to interact with the database.
    Returns:
        The deleted comment if the user is admin or moderator, otherwise returns a message saying that you can't delete
        comments.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if user.admin or user.moderator:
        if comment:
            db.delete(comment)
            db.commit()
        return comment
    else:
        return {"message": "You can't delete the comment."}
