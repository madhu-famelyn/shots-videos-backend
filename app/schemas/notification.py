from pydantic import BaseModel, Field
from typing import Optional

class NotificationSchema(BaseModel):
    id: str
    type: str = "drop"
    title: str
    body: str
    isRead: bool = Field(default=False, alias="is_read")
    targetId: Optional[str] = Field(default=None, alias="target_id")
    createdAt: str = Field(alias="created_at")

    class Config:
        populate_by_name = True
