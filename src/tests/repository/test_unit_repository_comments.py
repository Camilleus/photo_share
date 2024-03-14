import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Comment, User
from src.schemas import CommentModel, CommentResponse
from src.repository.comments import (
    get_comment,
    get_comments,
    create_comment,
    update_comment,
    remove_comment
)


class TestUnitRepositoryComments(unittest.IsolatedAsyncioTestCase):

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
        self.comment1 = Comment(
            id=1,
            user_id=1,
            picture_id=1,
            content="Test comment 1",
            created_at="2000-03-15T00:00:00"
        )
        self.comment2 = Comment(
            id=2,
            user_id=1,
            picture_id=1,
            content="Test comment 2",
            created_at="2006-03-15T00:00:00"
        )
        self.comment3 = Comment(
            id=3,
            user_id=2,
            picture_id=2,
            content="Test comment 3",
            created_at="2010-03-15T00:00:00"
        )

    async def test_get_all_comments_for_picture(self):
        comments = [self.comment1, self.comment2, self.comment3]
        skip = 0
        limit = 20
        self.session.query(Comment).filter().order_by(Comment.created_at.desc()).offset(skip).limit(limit).all.return_value = comments

        result = await get_comments(picture_id=1, db=self.session, skip=skip, limit=limit)

        self.assertEqual(result, comments)

    async def test_get_comment_found(self):
        comment = self.comment1
        self.session.query().filter().first.return_value = comment
        result = await get_comment(comment_id=1, user=self.user, db=self.session)
        self.assertEqual(result, comment)

    async def test_get_comment_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_comment(comment_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_comment(self):
        comment_model = CommentModel(
            content="Test comment")

        result = await create_comment(body=comment_model, picture_id=1, user=self.user, db=self.session)
        self.assertEqual(result.content, comment_model.content)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_comment_found(self):
        comment = CommentModel(
            content="Test content")
        self.session.query().filter().first.return_value = comment
        self.session.commit.return_value = None
        result = await update_comment(comment_id=1, body=comment, user=self.user, db=self.session)
        self.assertEqual(result, comment)

    async def test_update_comment_not_found(self):
        comment = CommentResponse(
            id=1,
            user_id=self.user.id,
            picture_id=1,
            content="Test content",
            created_at="2002-03-15T00:00:00",
            updated_at="2002-03-15T00:00:00")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_comment(comment_id=2, body=comment, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_remove_comment_found(self):
        comment = Comment()
        self.session.query().filter().first.return_value = comment
        result = await remove_comment(comment_id=1, user=self.user, db=self.session)
        self.assertEqual(result, comment)

    async def test_remove_comment_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_comment(comment_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)
