from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.user import CreatorSchema

class CommentSchema(BaseModel):
    id: str
    videoId: str = Field(alias="video_id")
    user: CreatorSchema
    text: str
    likes: int = 0
    isLiked: bool = Field(default=False, alias="is_liked")
    isOwn: bool = Field(default=False, alias="is_own")
    createdAt: str = Field(alias="created_at")

    class Config:
        populate_by_name = True

class CommentCreatePayload(BaseModel):
    text: str
