from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.user import CreatorSchema
from app.schemas.category import CategorySchema
from app.schemas.show import CastMemberSchema

class VideoSchema(BaseModel):
    id: str
    title: str
    description: str = ""
    videoUrl: str = Field(alias="video_url")
    thumbnailUrl: str = Field(alias="thumbnail_url")
    duration: int = 110
    views: int = 0
    likes: int = 0
    comments: int = Field(default=0, alias="comments_count")
    isLiked: bool = Field(default=False, alias="is_liked")
    isFollowing: bool = Field(default=False, alias="is_following")
    creator: CreatorSchema
    category: CategorySchema
    createdAt: str = Field(alias="created_at")
    seriesId: Optional[str] = Field(default=None, alias="series_id")
    seriesTitle: Optional[str] = Field(default=None, alias="series_title")
    episodeNumber: Optional[int] = Field(default=None, alias="episode_number")
    totalEpisodes: Optional[int] = Field(default=None, alias="total_episodes")
    language: Optional[str] = "भोजपुरी"
    clapsCount: Optional[int] = Field(default=0, alias="claps_count")
    cast: Optional[List[CastMemberSchema]] = []
    is18Plus: Optional[bool] = Field(default=False, alias="is_18_plus")
    badge: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True

class PaginatedVideos(BaseModel):
    items: List[VideoSchema]
    page: int
    limit: int
    total: int
    hasMore: bool

class HistoryEntrySchema(BaseModel):
    video: VideoSchema
    progress: float
    watchedAt: str

class TrackEventPayload(BaseModel):
    event: Optional[str] = "view"
    progress: Optional[float] = 0.0

class ReportPayload(BaseModel):
    reason: str
    description: Optional[str] = None
