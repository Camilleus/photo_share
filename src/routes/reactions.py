from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ReactionName
from src.services.auth import auth_service
from src.repository import reactions as repository_reactions


router = APIRouter(prefix="/reactions", tags=["reactions"])


@router.post("/{reaction}", status_code=status.HTTP_201_CREATED)
async def add_reaction_to_comment(
        comment_id: int,
        reaction: ReactionName,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    The add_reaction_to_comment function adds a reaction to a comment.
    Parameters:
        comment_id (int): Specify the comment to which we want to add a reaction
        reaction (ReactionName): Get the reaction name from the user
        current_user (User): Get the user who is logged in
        db (Session): Get a database session
    Returns:
        Information: "The reaction was added"
    """
    return await repository_reactions.add_reaction_to_comment(comment_id, reaction, current_user, db)


@router.delete("/{reaction}")
async def remove_reaction(
        comment_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    The remove_reaction function removes a reaction from a comment.
    Parameters:
        comment_id (int): The id of the comment to remove the reaction from.
        current_user (User): The user removing the reaction.
        db (Session): Get the database session
    Returns:
        A message if the comment has no reaction, else it removes the user's reaction from that comment
    """
    return await repository_reactions.remove_reaction_from_comment(comment_id, current_user, db)


@router.get("/{comment_id}")
async def get_reactions(
        comment_id: int,
        db: Session = Depends(get_db)
):
    """
    The get_reactions function returns a dict of all users and their reactions for a given comment.
    Parameters:
        comment_id (int): Get the reactions of a specific comment
        db (Session): Get the database session
    Returns:
        A list of users with their reactions for a comment
    """
    reactions = await repository_reactions.get_reactions(comment_id, db)
    return reactions


@router.get("/number/{comment_id}")
async def get_number_of_reactions(
        comment_id: int,
        db: Session = Depends(get_db)
):
    """
    The get_number_of_reactions function returns the numbers of reactions for a given comment.
    Parameters:
        comment_id (int): The id of the comment to get reactions from.
        db (Session): Pass the database session to the function
    Returns:
        The numbers of reactions for a comment
    """
    reactions = await repository_reactions.get_number_of_reactions(comment_id, db)
    return reactions
