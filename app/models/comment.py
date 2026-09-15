from sqlalchemy import Column, String, Integer, Text, DateTime
from datetime import datetime
from app.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, index=True)
    video_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    user_name = Column(String, nullable=False)
    user_username = Column(String, nullable=False)
    user_avatar = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class CommentLike(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    comment_id = Column(String, index=True)
