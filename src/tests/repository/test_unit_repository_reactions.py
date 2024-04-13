import unittest
from collections import Counter, OrderedDict
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Reaction, User

from src.repository.reactions import (
    add_reaction_to_comment,
    remove_reaction_from_comment,
    get_reactions,
    get_number_of_reactions
)


class TestUnitRepositoryReactions(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1,
            username="Username",
            email="username@example.com",
            password="password",
            created_at="2000-02-02T00:00:00",
            avatar=None,
            refresh_token="refresh_token",
            confirmed=False
        )
        self.reaction_1 = Reaction(
            id=1,
            comment_id=1,
            data={"like": [1]}
        )
        self.reaction_2 = Reaction(
            id=2,
            comment_id=2,
            data={"like": [1, 4, 8], "wow": [2, 3], "haha": [5, 7, 10, 13]}
        )

    # async def test_get_all_reactions_for_comment_found(self):
    #     reaction_record = self.reaction_1
    #     self.session.query(Reaction).filter(Reaction.comment_id == 1).first.return_value = reaction_record
    #     self.session.query(User).filter(User.id == 1).first.return_value = self.user
    #
    #     result = await get_reactions(comment_id=1, db=self.session)
    #
    #     expected_reactions = {}
    #     for react, users in reaction_record.data.items():
    #         for user_id in users:
    #             user = self.session.query(User).filter(User.id == user_id).first()
    #             if user:
    #                 expected_reactions[user.username] = react
    #
    #     self.assertEqual(result, expected_reactions)

    async def test_get_all_reactions_for_comment_not_found(self):
        self.session.query(Reaction).filter().first.return_value = None
        result = await get_reactions(comment_id=1, db=self.session)
        self.assertEqual(result, {})

    async def test_get_number_of_reactions_found(self):
        reactions = self.reaction_2
        self.session.query().filter().first.return_value = reactions
        reactions_data = reactions.data
        number_of_reactions = Counter()
        for react, users in reactions_data.items():
            number_of_reactions[react] = len(users)
        numbers_of_reactions = OrderedDict(number_of_reactions.most_common())
        result = await get_number_of_reactions(comment_id=2, db=self.session)
        self.assertEqual(result, numbers_of_reactions)

    async def test_get_number_of_reactions_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_number_of_reactions(comment_id=2, db=self.session)
        self.assertEqual(result, {"message": "No reaction for comment"})

    async def test_add_reaction_if_not_record(self):
        result = await add_reaction_to_comment(comment_id=1, reaction="like", user=self.user, db=self.session)
        self.assertEqual(result, {"message": "The reaction was added"})

    async def test_remove_reaction_record_found(self):
        reactions = self.reaction_1
        self.session.query().filter().first.return_value = reactions
        result = await remove_reaction_from_comment(comment_id=1, user=self.user, db=self.session)
        self.assertEqual(result, {"message": "Reaction was deleted"})

    async def test_remove_reaction_from_data_found(self):
        reactions = self.reaction_2
        self.session.query().filter().first.return_value = reactions
        result = await remove_reaction_from_comment(comment_id=2, user=self.user, db=self.session)
        self.assertEqual(result, {"message": "Reaction was deleted"})

    async def test_remove_reaction_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_reaction_from_comment(comment_id=1, user=self.user, db=self.session)
        self.assertEqual(result, {"message": "No reaction for comment"})
