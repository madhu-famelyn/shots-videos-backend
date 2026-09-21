from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.database import Base


class ModerationReport(Base):
    __tablename__ = "moderation_reports"

    id = Column(String, primary_key=True, index=True)
    video_id = Column(String, index=True, nullable=False)
    video_title = Column(String, nullable=False)
    reason = Column(String, nullable=False)          # nudity | copyright | spam | violence | other
    reports_count = Column(Integer, default=1)
    status = Column(String, default="pending", index=True)  # pending | approved | removed
    note = Column(String, nullable=True)
    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
