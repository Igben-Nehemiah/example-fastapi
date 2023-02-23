from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Union

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class CreatePostDto(PostBase):
    pass


class UpdatePostDto(PostBase):
    title: str
    content: str
    published: bool


class UserResponseDto(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


class PostResponseDto(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponseDto

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: PostResponseDto
    votes: int

    class Config:
        orm_mode = True

class CreateUserDto(BaseModel):
    email: EmailStr
    password: str



class UserLoginDto(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Union[str, None]
    

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
