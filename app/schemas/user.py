from pydantic import BaseModel, Field
from typing import Optional

class CreatorSchema(BaseModel):
    id: str
    name: str
    username: str
    avatar: str
    followers: int = 0
    isFollowing: bool = Field(default=False, alias="is_following")

    class Config:
        populate_by_name = True
        from_attributes = True

class UserProfileSchema(CreatorSchema):
    email: Optional[str] = ""
    phone: Optional[str] = ""
    bio: Optional[str] = ""
    following: int = 0
    totalLikes: int = Field(default=0, alias="total_likes")

    class Config:
        populate_by_name = True
        from_attributes = True

class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
