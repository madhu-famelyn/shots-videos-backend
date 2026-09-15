from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationSchema
from app.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationSchema])
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    if not notifs:
        # Provide welcoming Bhojpuri notification
        return [
            NotificationSchema(
                id="notif_welcome",
                type="drop",
                title="🔥 Welcome to Echo Reels Bhojpuri!",
                body="Pawan Singh & Khesari Lal's latest 2-minute micro-drama episodes are now streaming.",
                isRead=False,
                targetId="trend-1",
                createdAt="2026-09-10T12:00:00Z"
            )
        ]
    return [
        NotificationSchema(
            id=n.id,
            type=n.type,
            title=n.title,
            body=n.body,
            isRead=n.is_read,
            targetId=n.target_id,
            createdAt=n.created_at.isoformat() if n.created_at else "2026-09-10T12:00:00Z"
        )
        for n in notifs
    ]

@router.post("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"success": True}
