from pydantic import BaseModel
from fastapi_users import schemas
import uuid

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    title: str
    content: str

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    post_id: uuid.UUID
    content: str
    created_at: str  # We'll convert datetime to string in the endpoint or use Config


class LikeCreate(BaseModel):
    pass  # No body needed for like toggle


class LikeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    post_id: uuid.UUID