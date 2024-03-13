import datetime

from sqlalchemy import Column, Integer, String, func, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.sqltypes import DateTime, Boolean, JSON

Base = declarative_base()


class PictureTagsAssociation(Base):
    """
    SQLAlchemy model representing the association between pictures and tags.

    Attributes:
        picture_id (int): Foreign key referencing the id of the picture.
        tag_id (int): Foreign key referencing the id of the tag.
    """
    __tablename__ = 'picture_tags_association'

    picture_id = Column(Integer, ForeignKey('picture.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)


class Tag(Base):
    """
    SQLAlchemy model representing a tag.

    Attributes:
        id (int): Primary key for the tag.
        name (str): Name of the tag (unique).
    """
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    pictures = relationship('Picture', secondary='picture_tags_association', back_populates='tags')


class Picture(Base):
    """
    SQLAlchemy model representing a picture.

    Attributes:
        id (int): Primary key for the picture.
        user_id (int): Foreign key referencing the id of the user who uploaded the picture.
        user (User): Relationship with the User model representing the uploader of the picture.
        tags (list[Tag]): Relationship with the Tag model representing tags associated with the picture.
        comments (list[Comment]): Relationship with the Comment model representing comments on the picture.
        picture_url (str): URL of the original picture.
        picture_edited_url (str): URL of the edited picture (nullable).
        qr_code_picture (str): URL of the QR code associated with the original picture (nullable).
        qr_code_picture_edited (str): URL of the QR code associated with the edited picture (nullable).
        description (str): Description of the picture (nullable).
        created_at (DateTime): Timestamp indicating when the picture was created.
    """
    __tablename__ = "picture"

    id = Column(Integer, primary_key=True, index=True)
    picture_json = Column(JSON, nullable=True)
    picture_url = Column(String(255), nullable=False)
    picture_edited_json = Column(JSON, nullable=True)
    picture_edited_url = Column(String(255), nullable=True)
    qr_code_picture = Column(String(255), nullable=True)
    qr_code_picture_edited = Column(String(255), nullable=True)
    description = Column(String, nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
    user_id = Column('user_id', ForeignKey('user.id', ondelete='CASCADE'), default=None)

    user = relationship('User', back_populates='pictures')
    tags = relationship('Tag', secondary='picture_tags_association', back_populates='pictures')
    comments = relationship('Comment', back_populates='picture')
    ratings = relationship('Rating', back_populates='picture')

    @hybrid_property
    def average_rating(self):
        if self.ratings:
            return sum(rat.rat for rat in self.ratings) / len(self.ratings)
        return None


class Rating(Base):
    """
    Represents a rating entity associated with a specific picture and user.

    Attributes:
        id (int): The unique identifier for the rating instance.
        picture_id (int): The identifier of the picture this rating is associated with.
        user_id (int): The identifier of the user who provided the rating.
        rat (int): The numerical rating value. This value is optional and can be null to represent the absence of a rating.
        picture (relationship): Establishes a relationship to the Picture object this rating is associated with. Allows direct access to the Picture instance.
        user (relationship): Establishes a relationship to the User object who provided this rating. Allows direct access to the User instance.

    The `picture` and `user` relationships create a direct link between the Rating instance and the associated Picture and User instances, respectively. This setup facilitates easy navigation and manipulation of related data within the application's ORM layer.
    """
    __tablename__ = "rating"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    picture_id = Column(Integer, ForeignKey('picture.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    rat = Column(Integer, nullable=True)

    picture = relationship('Picture', back_populates='ratings')
    user = relationship('User', back_populates='ratings')


class Comment(Base):
    """
    SQLAlchemy model representing a comment.

    Attributes:
        id (int): Primary key for the comment.
        user_id (int): Foreign key referencing the id of the user who posted the comment.
        picture_id (int): Foreign key referencing the id of the picture associated with the comment.
        content (str): Content of the comment.
        picture (Picture): Relationship with the Picture model representing the associated picture.
        user (User): Relationship with the User model representing the user who posted the comment.
    """
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    picture_id = Column(Integer, ForeignKey('picture.id', ondelete='CASCADE'))
    content = Column(String(255), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, onupdate=datetime.datetime.now)

    reactions = relationship('Reaction', back_populates='comment')
    picture = relationship('Picture', back_populates='comments')
    user = relationship('User', back_populates='comments')


class Reaction(Base):
    """
    SQLAlchemy model representing a reaction on a comment.

    Attributes:
        id (int): Primary key for the like.
        comment_id (int): Foreign key referencing the id of the liked comment.
        data (json): Dict of reactions with lists of users_id as values for a given reaction.
        comment (Comment): Relationship with the Comment model representing the liked comment.
    """
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comment_id = Column(Integer, ForeignKey('comment.id', ondelete='CASCADE'))
    data = Column(JSON)

    comment = relationship('Comment', back_populates='reactions')


class User(Base):
    """
    SQLAlchemy model representing a user.

    Attributes:
        id (int): Primary key for the user.
        username (str): Username of the user.
        email (str): Email address of the user (unique).
        password (str): Password of the user.
        created_at (DateTime): Timestamp indicating when the user was created.
        avatar (str): Filepath to the user's avatar (nullable).
        refresh_token (str): Refresh token for the user (nullable).
        confirmed (bool): Flag indicating whether the user is confirmed.
        admin (bool): Flag indicating whether the user has admin privileges.
        moderator (bool): Flag indicating whether the user has moderator permissions.
        pictures (list[Picture]): Relationship with the Picture model representing pictures uploaded by the user.
        comments (list[Comment]): Relationship with the Comment model representing comments posted by the user.
        sent_messages (list[Message]): Relationship with the Message model representing messages sent by the user.
        received_messages (list[Message]): Relationship with the Message model representing messages received by the user.
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(2048), nullable=True)
    confirmed = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    moderator = Column(Boolean, default=False)
    ban_status = Column(Boolean, default=False)
    qr_code = Column(String(255), nullable=True)

    pictures = relationship('Picture', back_populates='user')
    comments = relationship('Comment', back_populates='user')
    sent_messages = relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')
    received_messages = relationship('Message', back_populates='receiver', foreign_keys='Message.receiver_id')
    ratings = relationship('Rating', back_populates='user')

    def dict(self):
        """
        Convert user data to a dictionary.

        Returns:
            dict: User data as a dictionary.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "avatar": self.avatar,
            "refresh_token": self.refresh_token,
            "confirmed": self.confirmed,
            "admin": self.admin,
            "moderator": self.moderator
        }


class Message(Base):
    """
    SQLAlchemy model representing a message.

    Attributes:
        id (int): Primary key for the message.
        sender_id (int): Foreign key referencing the id of the user who sent the message.
        receiver_id (int): Foreign key referencing the id of the user who received the message.
        content (str): Content of the message.
        timestamp (DateTime): Timestamp indicating when the message was sent.
        sender (User): Relationship with the User model representing the sender of the message.
        receiver (User): Relationship with the User model representing the receiver of the message.
    """
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('user.id'))
    receiver_id = Column(Integer, ForeignKey('user.id'))
    content = Column(String(255), nullable=False)
    timestamp = Column('timestamp', DateTime, default=func.now())

    sender = relationship('User', back_populates='sent_messages', foreign_keys=[sender_id])
    receiver = relationship('User', back_populates='received_messages', foreign_keys=[receiver_id])
