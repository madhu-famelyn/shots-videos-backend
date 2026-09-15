from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video import Video
from app.models.user import User
from app.schemas.video import VideoSchema
from app.schemas.user import CreatorSchema
from app.schemas.category import CategorySchema
from app.routers.videos import format_video
from app.routers.categories import CATEGORIES

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("")
def search(
    q: str = Query("", min_length=0),
    db: Session = Depends(get_db)
):
    query_str = q.strip().lower()
    if not query_str:
        return {"videos": [], "creators": [], "categories": []}

    videos = db.query(Video).filter(
        (Video.title.ilike(f"%{query_str}%")) |
        (Video.description.ilike(f"%{query_str}%")) |
        (Video.creator_name.ilike(f"%{query_str}%"))
    ).all()

    matched_categories = [
        CategorySchema(**c) for c in CATEGORIES
        if query_str in c["name"].lower() or query_str in c["slug"]
    ]

    seen = set()
    creators = []
    for v in videos:
        if v.creator_id not in seen:
            seen.add(v.creator_id)
            creators.append(CreatorSchema(
                id=v.creator_id,
                name=v.creator_name,
                username=v.creator_username,
                avatar=v.creator_avatar,
                followers=150000
            ))

    return {
        "videos": [format_video(v) for v in videos],
        "creators": creators,
        "categories": matched_categories
    }
