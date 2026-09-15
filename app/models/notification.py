from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    type = Column(String, default="drop")
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    target_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
