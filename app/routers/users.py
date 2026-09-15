from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, Follow
from app.models.video import Video, VideoHistory
from app.schemas.user import UserProfileSchema, UserUpdateSchema
from app.schemas.video import VideoSchema, HistoryEntrySchema
from app.dependencies import get_current_user
from app.routers.videos import format_video

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserProfileSchema)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserProfileSchema(
        id=current_user.id,
        name=current_user.name,
        username=current_user.username,
        avatar=current_user.avatar,
        email=current_user.email or "",
        bio=current_user.bio or "",
        followers=current_user.followers or 0,
        following=current_user.following or 0,
        totalLikes=current_user.total_likes or 0,
        isFollowing=False
    )

@router.put("/me", response_model=UserProfileSchema)
def update_profile(
    payload: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if payload.name:
        current_user.name = payload.name
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.avatar:
        current_user.avatar = payload.avatar
    
    db.commit()
    db.refresh(current_user)
    return UserProfileSchema(
        id=current_user.id,
        name=current_user.name,
        username=current_user.username,
        avatar=current_user.avatar,
        email=current_user.email or "",
        bio=current_user.bio or "",
        followers=current_user.followers or 0,
        following=current_user.following or 0,
        totalLikes=current_user.total_likes or 0,
        isFollowing=False
    )

@router.get("/me/videos", response_model=List[VideoSchema])
def get_user_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).limit(10).all()
    return [format_video(v) for v in videos]

@router.get("/me/history", response_model=List[HistoryEntrySchema])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entries = db.query(VideoHistory).filter(VideoHistory.user_id == current_user.id).order_by(VideoHistory.watched_at.desc()).all()
    res = []
    for e in entries:
        v = db.query(Video).filter(Video.id == e.video_id).first()
        if v:
            res.append(HistoryEntrySchema(
                video=format_video(v),
                progress=e.progress or 0.5,
                watchedAt=e.watched_at.isoformat() if e.watched_at else "2026-09-10T12:00:00Z"
            ))
    return res

@router.post("/{user_id}/follow")
def follow_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Follow).filter(Follow.follower_id == current_user.id, Follow.following_id == user_id).first()
    if not existing:
        db.add(Follow(follower_id=current_user.id, following_id=user_id))
        target_user = db.query(User).filter(User.id == user_id).first()
        if target_user:
            target_user.followers = (target_user.followers or 0) + 1
        current_user.following = (current_user.following or 0) + 1
        db.commit()
    return {"success": True}

@router.delete("/{user_id}/follow")
def unfollow_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Follow).filter(Follow.follower_id == current_user.id, Follow.following_id == user_id).first()
    if existing:
        db.delete(existing)
        target_user = db.query(User).filter(User.id == user_id).first()
        if target_user and target_user.followers > 0:
            target_user.followers -= 1
        if current_user.following > 0:
            current_user.following -= 1
        db.commit()
    return {"success": True}
