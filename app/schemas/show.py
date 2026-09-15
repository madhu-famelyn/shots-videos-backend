from pydantic import BaseModel, Field
from typing import List, Optional

class CastMemberSchema(BaseModel):
    name: str
    role: str
    avatar: str

class EpisodeSchema(BaseModel):
    id: str
    episodeNumber: int = Field(alias="episode_number")
    title: str
    duration: int = 120
    thumbnailUrl: str = Field(alias="thumbnail_url")
    videoUrl: str = Field(alias="video_url")
    views: int = 0
    claps: int = 0

    class Config:
        populate_by_name = True

class ShowSchema(BaseModel):
    id: str
    title: str
    synopsis: str
    coverImage: str = Field(alias="cover_image")
    genre: str
    language: str = "भोजपुरी"
    rating: float = 4.8
    totalEpisodes: int = Field(default=8, alias="total_episodes")
    director: str = "Bhojpuri Studios"
    cast: List[CastMemberSchema] = []
    episodes: List[EpisodeSchema] = []
    featured: Optional[bool] = False
    is18Plus: Optional[bool] = Field(default=False, alias="is_18_plus")
    isComingSoon: Optional[bool] = Field(default=False, alias="is_coming_soon")
    releaseDate: Optional[str] = Field(default=None, alias="release_date")
    sectionCategory: Optional[str] = Field(default="trending", alias="section_category")
    badge: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True
