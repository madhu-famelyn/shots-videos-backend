import json
from sqlalchemy import Column, String, Integer, Float, Boolean, Text
from app.database import Base

class Show(Base):
    __tablename__ = "shows"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    synopsis = Column(Text, nullable=False)
    cover_image = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    language = Column(String, default="भोजपुरी")
    rating = Column(Float, default=4.8)
    total_episodes = Column(Integer, default=8)
    director = Column(String, default="Bhojpuri Studios")
    featured = Column(Boolean, default=False)
    is_18_plus = Column(Boolean, default=False)
    is_coming_soon = Column(Boolean, default=False)
    release_date = Column(String, nullable=True)
    section_category = Column(String, default="trending", index=True)
    badge = Column(String, nullable=True)
    cast_json = Column(Text, default="[]")
    episodes_json = Column(Text, default="[]")

class CastMember(Base):
    __tablename__ = "cast_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    show_id = Column(String, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    avatar = Column(String, nullable=False)

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(String, primary_key=True, index=True)
    show_id = Column(String, index=True)
    episode_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    duration = Column(Integer, default=120)
    thumbnail_url = Column(String, nullable=False)
    video_url = Column(String, nullable=False)
    views = Column(Integer, default=0)
    claps = Column(Integer, default=0)
