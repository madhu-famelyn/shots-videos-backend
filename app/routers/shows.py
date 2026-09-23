import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.show import Show
from app.models.video import Video
from app.schemas.show import ShowSchema, CastMemberSchema, EpisodeSchema

router = APIRouter(prefix="/shows", tags=["Shows"])

def format_video_as_show(v: Video) -> ShowSchema:
    vert = (v.vertical or v.category_id or "trending").lower()
    if vert in ("mature", "18_plus", "18+"):
        section = "18_plus"
    elif vert in ("drama", "romance"):
        section = "drama"
    elif vert in ("coming_soon", "trailer"):
        section = "coming_soon"
    elif vert in ("shorts", "short_serial", "episode", "comedy"):
        section = "short_serial"
    elif vert in ("thriller", "action", "crime"):
        section = "thriller"
    else:
        section = "trending"

    return ShowSchema(
        id=v.id,
        title=v.title,
        synopsis=v.description or f"Watch this original Bhojpuri {v.vertical or 'entertainment'} video.",
        coverImage=v.thumbnail_url or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&h=900&fit=crop",
        genre=(v.category_name or v.vertical or "Bhojpuri").capitalize(),
        language=v.language or "भोजपुरी",
        rating=4.9,
        totalEpisodes=v.total_episodes or 1,
        director=v.creator_name or "Echo Reels Studio",
        cast=[CastMemberSchema(name=v.creator_name or "Creator", role="Creator", avatar=v.creator_avatar or "")],
        episodes=[EpisodeSchema(
            id=f"{v.id}_ep1",
            episodeNumber=v.episode_number or 1,
            title=v.title,
            duration=v.duration or 60,
            thumbnailUrl=v.thumbnail_url or "",
            videoUrl=v.video_url or "",
            views=v.views or 0,
            claps=v.claps_count or 0
        )],
        featured=True,
        is18Plus=v.is_18_plus or False,
        isComingSoon=False,
        releaseDate=None,
        sectionCategory=section,
        badge=v.badge or "🔥 Trending"
    )

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
    results = []
    # 1. Any direct Show entries
    q_shows = db.query(Show)
    if category and category != "all":
        q_shows = q_shows.filter(Show.section_category == category)
    if featured is not None:
        q_shows = q_shows.filter(Show.featured == featured)
    for s in q_shows.all():
        results.append(format_show(s))

    # 2. Uploaded Videos from Admin (only those with a real video_url)
    q_vids = db.query(Video).filter(Video.status == "published", Video.video_url != "", Video.video_url != None)
    for v in q_vids.order_by(Video.created_at.desc()).all():
        show_item = format_video_as_show(v)
        if category and category != "all" and show_item.sectionCategory != category:
            continue
        results.append(show_item)

    return results

@router.get("/trending", response_model=List[ShowSchema])
def get_trending_shows(db: Session = Depends(get_db)):
    return list_shows(category="trending", db=db)

@router.get("/category/{cat_id}", response_model=List[ShowSchema])
def get_shows_by_category(cat_id: str, db: Session = Depends(get_db)):
    return list_shows(category=cat_id, db=db)

@router.get("/{show_id}", response_model=ShowSchema)
def get_show(show_id: str, db: Session = Depends(get_db)):
    show = db.query(Show).filter(Show.id == show_id).first()
    if show:
        return format_show(show)
    
    video = db.query(Video).filter(Video.id == show_id).first()
    if video:
        return format_video_as_show(video)
        
    raise HTTPException(status_code=404, detail="Content not found")

