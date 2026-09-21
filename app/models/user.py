from sqlalchemy import Column, String, Integer, Boolean, Text
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    avatar = Column(String, default="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop")
    bio = Column(Text, default="Bhojpuri Cinema & Reels Lover 🎬")
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    is_following = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    verified = Column(Boolean, default=False)          # ← creator verified badge

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    follower_id = Column(String, index=True)
    following_id = Column(String, index=True)
