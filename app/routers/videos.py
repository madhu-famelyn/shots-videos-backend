import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.video import Video, VideoLike, VideoHistory
from app.models.comment import Comment
from app.models.user import User
from app.schemas.video import VideoSchema, PaginatedVideos, TrackEventPayload, ReportPayload
from app.schemas.user import CreatorSchema
from app.schemas.category import CategorySchema
from app.schemas.comment import CommentSchema
from app.dependencies import get_optional_user, get_current_user

router = APIRouter(prefix="/videos", tags=["Videos"])

def format_video(v: Video, is_liked: bool = False, is_following: bool = False) -> VideoSchema:
    return VideoSchema(
        id=v.id,
        title=v.title,
        description=v.description or "",
        videoUrl=v.video_url,
        thumbnailUrl=v.thumbnail_url,
        duration=v.duration or 110,
        views=v.views or 0,
        likes=v.likes or 0,
        comments=v.comments_count or 0,
        isLiked=is_liked,
        isFollowing=is_following,
        creator=CreatorSchema(
            id=v.creator_id,
            name=v.creator_name,
            username=v.creator_username,
            avatar=v.creator_avatar,
            followers=150000,
            isFollowing=is_following
        ),
        category=CategorySchema(
            id=v.category_id,
            name=v.category_name,
            slug=v.category_id
        ),
        createdAt=v.created_at.isoformat() if v.created_at else "2026-09-10T12:00:00Z",
        seriesId=v.series_id,
        seriesTitle=v.series_title,
        episodeNumber=v.episode_number,
        totalEpisodes=v.total_episodes,
        language=v.language or "भोजपुरी",
        clapsCount=v.claps_count or 0,
        is18Plus=v.is_18_plus or False,
        badge=v.badge
    )

@router.get("/feed", response_model=PaginatedVideos)
def get_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=50),
    category_id: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    query = db.query(Video)
    if category_id and category_id != "all":
        query = query.filter(Video.category_id == category_id)
    
    total = query.count()
    offset = (page - 1) * limit
    videos = query.offset(offset).limit(limit).all()

    liked_video_ids = set()
    if current_user:
        likes = db.query(VideoLike.video_id).filter(VideoLike.user_id == current_user.id).all()
        liked_video_ids = {l[0] for l in likes}

    items = [format_video(v, is_liked=(v.id in liked_video_ids)) for v in videos]
    return PaginatedVideos(
        items=items,
        page=page,
        limit=limit,
        total=total,
        hasMore=(offset + limit < total)
    )

@router.get("/{video_id}", response_model=VideoSchema)
def get_video(
    video_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    v = db.query(Video).filter(Video.id == video_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")
    
    is_liked = False
    if current_user:
        like = db.query(VideoLike).filter(VideoLike.user_id == current_user.id, VideoLike.video_id == video_id).first()
        is_liked = bool(like)
    
    return format_video(v, is_liked=is_liked)

@router.post("/{video_id}/like")
def like_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    existing = db.query(VideoLike).filter(VideoLike.user_id == current_user.id, VideoLike.video_id == video_id).first()
    if not existing:
        db.add(VideoLike(user_id=current_user.id, video_id=video_id))
        video.likes = (video.likes or 0) + 1
        db.commit()
    return {"success": True, "likes": video.likes}

@router.delete("/{video_id}/like")
def unlike_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    existing = db.query(VideoLike).filter(VideoLike.user_id == current_user.id, VideoLike.video_id == video_id).first()
    if existing:
        db.delete(existing)
        if video and video.likes > 0:
            video.likes -= 1
        db.commit()
    return {"success": True}

@router.post("/{video_id}/events")
def track_event(
    video_id: str,
    payload: TrackEventPayload,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if video:
        video.views = (video.views or 0) + 1
        if current_user:
            hist = db.query(VideoHistory).filter(VideoHistory.user_id == current_user.id, VideoHistory.video_id == video_id).first()
            if not hist:
                db.add(VideoHistory(user_id=current_user.id, video_id=video_id, progress=payload.progress))
            else:
                hist.progress = payload.progress
        db.commit()
    return {"success": True}

@router.post("/{video_id}/report")
def report_video(video_id: str, payload: ReportPayload):
    return {"success": True, "message": "Report submitted"}

@router.get("/{video_id}/comments")
def list_video_comments(
    video_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    comments = db.query(Comment).filter(Comment.video_id == video_id).all()
    res = []
    for c in comments:
        res.append(CommentSchema(
            id=c.id,
            videoId=c.video_id,
            user=CreatorSchema(
                id=c.user_id,
                name=c.user_name,
                username=c.user_username,
                avatar=c.user_avatar,
                followers=100
            ),
            text=c.text,
            likes=c.likes or 0,
            isLiked=False,
            isOwn=(current_user.id == c.user_id) if current_user else False,
            createdAt=c.created_at.isoformat() if c.created_at else "2026-09-10T12:00:00Z"
        ))
    return res

@router.post("/{video_id}/comments")
def create_comment(
    video_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    text = payload.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Comment text cannot be empty")
    
    comment_id = f"cm_{uuid.uuid4().hex[:8]}"
    comment = Comment(
        id=comment_id,
        video_id=video_id,
        user_id=current_user.id,
        user_name=current_user.name,
        user_username=current_user.username,
        user_avatar=current_user.avatar,
        text=text
    )
    db.add(comment)
    
    video = db.query(Video).filter(Video.id == video_id).first()
    if video:
        video.comments_count = (video.comments_count or 0) + 1
    
    db.commit()
    db.refresh(comment)

    return CommentSchema(
        id=comment.id,
        videoId=comment.video_id,
        user=CreatorSchema(
            id=current_user.id,
            name=current_user.name,
            username=current_user.username,
            avatar=current_user.avatar
        ),
        text=comment.text,
        likes=0,
        isLiked=False,
        isOwn=True,
        createdAt=comment.created_at.isoformat()
    )
