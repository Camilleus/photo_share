from collections import Counter, OrderedDict

from sqlalchemy.orm import Session

from src.database.models import Reaction, User


async def add_reaction_to_comment(comment_id: int, reaction: str, user: User, db: Session):
    """
    The add_reaction_to_comment function adds or updates a reaction to a comment.
        Parameters:
            comment_id (int): The id of the comment that is being reacted to.
            reaction (str): The type of reaction that is being added.This can be one of "like", "love", "haha",
                            "wow" or "dislike".
            user (User): A User object representing the user who is adding the reaction. This should be obtained
                            from get_current_user().
            db: Session: Access the database
        Returns:
            Information: "The reaction was added"
    """
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    if not reaction_record:
        new_reaction = Reaction(comment_id=comment_id, data={reaction: [user.id]})
        db.add(new_reaction)
    else:
        await update_reaction_to_comment(comment_id, reaction, user, db)
    db.commit()
    return {"message": "The reaction was added"}


async def update_reaction_to_comment(comment_id: int, reaction: str, user: User, db: Session):
    """
    The update_reaction_to_comment function updates reaction which was added to comment by user.
    Parameters:
        comment_id (int): Identify the comment that is being reacted to
        reaction (str): Determine which reaction to add
        user (User): Get the user id of the person who reacted to a comment
        db (Session): Pass the database session to the function
    Returns:
        The updated reaction_data.
    """
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    reaction_data = reaction_record.data
    reaction_data_copy = reaction_data.copy()
    for react, users in reaction_data_copy.items():
        if user.id in users:
            users.remove(user.id)
        if not users:
            del reaction_data[react]
    if reaction not in reaction_data:
        reaction_data[reaction] = [user.id]
    else:
        reaction_data[reaction].append(user.id)
    db.query(Reaction).filter(Reaction.comment_id == comment_id).update({"data": reaction_data})


async def remove_reaction_from_comment(comment_id: int, user: User, db: Session):
    """
    The remove_reaction_from_comment function removes a reaction from a comment.
    Parameters:
    comment_id (int): Identify the comment that is being reacted to
    user (User): Get the user id of the user who is reacting to a comment
    db (Session): Create a database session
    Returns:
        A message if the comment has no reaction, else it removes the user's reaction from that comment
    """
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    if not reaction_record:
        return {"message": "No reaction for comment"}
    else:
        reaction_data = reaction_record.data
        reaction_data_copy = reaction_data.copy()
        for react, users in reaction_data_copy.items():
            if user.id in users:
                users.remove(user.id)
            if not users:
                del reaction_data[react]
            if reaction_data:
                db.query(Reaction).filter(Reaction.comment_id == comment_id).update({"data": reaction_data})
            else:
                db.delete(reaction_record)
        db.commit()
        return {"message": "Reaction was deleted"}


async def get_reactions(comment_id: int, db: Session):
    """
    The get_reactions function takes in a comment_id and returns users and their reactions for that comment.
    Parameters:
        comment_id (int): Specify the comment id of the comment you want to get reactions for
        db (Session): Access the database
    Returns:
        A dictionary of the users and their reactions for the comment.
    """
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    if not reaction_record:
        return {"message": "No reaction for comment"}
    reaction_data = reaction_record.data
    reactions = {}
    for react, users in reaction_data.items():
        for user_id in users:
            user = db.query(User).filter(User.id == user_id).first()
            reactions[user.username] = react
    return reactions


async def get_number_of_reactions(comment_id: int, db: Session):
    """
    The get_number_of_reactions function takes in a comment_id and returns the numbers of reactions for that comment.
    Parameters:
        comment_id (int): Specify the comment id of the comment you want to get numbers of reactions for
        db: (Session): Pass the database session to the function
    Returns:
        A dictionary of reactions with the number of users who have reacted to a comment
    """
    reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
    if not reaction_record:
        return {"message": "No reaction for comment"}
    reaction_data = reaction_record.data
    number_of_reactions = Counter()
    for react, users in reaction_data.items():
        number_of_reactions[react] = len(users)
    return OrderedDict(number_of_reactions.most_common())

