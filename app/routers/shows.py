import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.show import Show
from app.schemas.show import ShowSchema, CastMemberSchema, EpisodeSchema

router = APIRouter(prefix="/shows", tags=["Shows"])

def format_show(s: Show) -> ShowSchema:
    cast_data = []
    if s.cast_json:
        try:
            cast_data = [CastMemberSchema(**c) for c in json.loads(s.cast_json)]
        except Exception:
            pass

    episodes_data = []
    if s.episodes_json:
        try:
            episodes_data = [EpisodeSchema(**e) for e in json.loads(s.episodes_json)]
        except Exception:
            pass

    return ShowSchema(
        id=s.id,
        title=s.title,
        synopsis=s.synopsis,
        coverImage=s.cover_image,
        genre=s.genre,
        language=s.language or "भोजपुरी",
        rating=s.rating or 4.8,
        totalEpisodes=s.total_episodes or 8,
        director=s.director or "Bhojpuri Studios",
        cast=cast_data,
        episodes=episodes_data,
        featured=s.featured or False,
        is18Plus=s.is_18_plus or False,
        isComingSoon=s.is_coming_soon or False,
        releaseDate=s.release_date,
        sectionCategory=s.section_category or "trending",
        badge=s.badge
    )

@router.get("", response_model=List[ShowSchema])
def list_shows(
    category: Optional[str] = Query(None),
    featured: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Show)
    if category and category != "all":
        q = q.filter(Show.section_category == category)
    if featured is not None:
        q = q.filter(Show.featured == featured)
    
    shows = q.all()
    return [format_show(s) for s in shows]

@router.get("/trending", response_model=List[ShowSchema])
def get_trending_shows(db: Session = Depends(get_db)):
    shows = db.query(Show).filter(Show.section_category == "trending").all()
    return [format_show(s) for s in shows]

@router.get("/category/{cat_id}", response_model=List[ShowSchema])
def get_shows_by_category(cat_id: str, db: Session = Depends(get_db)):
    shows = db.query(Show).filter(Show.section_category == cat_id).all()
    return [format_show(s) for s in shows]

@router.get("/{show_id}", response_model=ShowSchema)
def get_show(show_id: str, db: Session = Depends(get_db)):
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    return format_show(show)
