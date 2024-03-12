from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr
from enum import Enum, IntEnum


class UserModel(BaseModel):
    """
    Schema for user input during registration.
    """
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserDb(BaseModel):
    """
    Schema for user data retrieved from the database.
    """
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str | None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Schema for the response after user creation.
    """
    user: UserDb
    detail: str = "User successfully created"


class UserSearch(UserModel):
    keywords: Optional[List[str]] = None
    id: Optional[List[int]] = None
    username: Optional[List[str]] = None
    email: Optional[List[str]] = None

    class Config:
        from_attributes = True
        

class UserUpdateName(BaseModel):
    username: str = Field(min_length=5, max_length=16)


class AdminUserUpdateModel(BaseModel):
    """
    Schema for admin to update user data, excluding password, refresh_token and created_at fields.
    """
    username: Optional[str] = Field(None, min_length=5, max_length=16)
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    confirmed: Optional[bool] = None
    admin: Optional[bool] = None
    moderator: Optional[bool] = None


class TokenModel(BaseModel):
    """
    Schema for the response containing access and refresh tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Schema for the request containing an email address.
    """
    email: EmailStr


class PictureBase(BaseModel):
    description: Optional[str] | None


class PictureModel(PictureBase):
    tags: Optional[List[int]]


class PictureDB(BaseModel):
    id: int
    picture_url: Optional[str]
    rating: Optional[int]
    description: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class PictureDescription(BaseModel):
    description: Optional[str] | None


class PictureResponse(PictureBase):
    id: int
    picture_url: str | None
    average_rating: Optional[float] | None
    created_at: datetime
    tags: Optional[List[int]]
    qr_code_picture: Optional[str] | None

    class Config:
        orm_mode = True


class PictureSearch(PictureBase):
    keywords: Optional[List[str]] = None
    id: Optional[List[int]] = None
    user_id: Optional[List[int]] = None
    picture_name: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    class Config:
        from_attributes = True


class RatingValue(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    content: str


class MessageModel(MessageBase):
    id: int

    class Config:
        from_attributes = True


class MessageResponse(MessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class MessageSend(BaseModel):
    receiver_id: int
    content: str


class CommentModel(BaseModel):
    content: str = Field(min_length=1, max_length=300)


class CommentUpdate(CommentModel):
    updated_at: datetime | None


class CommentResponse(CommentUpdate):
    id: int
    user_id: int
    picture_id: int
    created_at: datetime

    class Config:
        from_attributes = True

        
class TagModel(BaseModel):
    """
    Schema for tag input during tag creation.
    """
    id: int
    name: str

class TagsResponseModel(BaseModel):
    """
    Response schema for the add_tags endpoint.
    """
    new_tags: List[TagModel]
    existing_tags: List[TagModel]
    


class ChangePasswordModel(BaseModel):
    """
    Schema for changing user password.

    Attributes:
    - current_password (str): The current password of the user.
    - new_password (str): The new password to be set.
    - confirm_password (str): Confirmation of the new password.
    """

    current_password: str
    new_password: str
    confirm_password: str


class ResetPasswordModel(BaseModel):
    """
    Schema for resetting user password.

    Attributes:
    - new_password (str): The new password to be set.
    - confirm_password (str): Confirmation of the new password.
    """
    
    new_password: str
    confirm_password: str


class PictureEdit(BaseModel):
    """
    Schema for editing picture parameters.

    Attributes:
    - improve (str, optional): The level of improvement to be applied to the picture (default: "0").
    - contrast (str, optional): The level of contrast adjustment to be applied (default: "0").
    - unsharp_mask (str, optional): The strength of the unsharp mask to be applied (default: "0").
    - brightness (str, optional): The level of brightness adjustment to be applied (default: "0").
    - gamma (str, optional): The gamma correction value to be applied (default: "0").
    - grayscale (bool, optional): Flag indicating whether grayscale effect should be applied (default: False).
    - redeye (bool, optional): Flag indicating whether redeye correction should be applied (default: False).
    - gen_replace (str, optional): Replacement value for generated text (default: "from_null;to_null").
    - gen_remove (str, optional): Prompt for removing generated text (default: "prompt_null").
    """

    improve: str = "0"
    contrast: str = "0"
    unsharp_mask: str = "0"
    brightness: str = "0"
    gamma: str = "0"
    grayscale: bool = False
    redeye: bool = False
    gen_replace: str = "from_null;to_null"
    gen_remove: str = "prompt_null"


class ReactionName(str, Enum):
    like = "like"
    love = "love"
    wow = "wow"
    haha = "haha"
    dislike = "dislike"
