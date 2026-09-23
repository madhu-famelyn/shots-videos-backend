from sqlalchemy import Column, String, Integer, Boolean, Text, Float, DateTime
from datetime import datetime
from app.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, default="")
    video_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=False)
    duration = Column(Integer, default=60)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    creator_id = Column(String, nullable=False, index=True)
    creator_name = Column(String, default="Admin")
    creator_username = Column(String, default="admin")
    creator_avatar = Column(String, default="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop")
    category_id = Column(String, default="shorts", index=True)
    category_name = Column(String, default="Shorts")
    series_id = Column(String, nullable=True)
    series_title = Column(String, nullable=True)
    episode_number = Column(Integer, nullable=True)
    total_episodes = Column(Integer, nullable=True)
    language = Column(String, default="bho")
    claps_count = Column(Integer, default=0)
    is_18_plus = Column(Boolean, default=False)
    badge = Column(String, nullable=True)
    status = Column(String, default="published", index=True)   # draft | published | processing | scheduled | rejected
    vertical = Column(String, default="entertainment", index=True)  # content vertical slug
    created_at = Column(DateTime, default=datetime.utcnow)

class VideoLike(Base):
    __tablename__ = "video_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    video_id = Column(String, index=True)

class VideoHistory(Base):
    __tablename__ = "video_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    video_id = Column(String, index=True)
    progress = Column(Float, default=0.0)
    watched_at = Column(DateTime, default=datetime.utcnow)
