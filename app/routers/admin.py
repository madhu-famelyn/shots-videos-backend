"""
Admin API Router — /api/admin/*
All endpoints are open for now (auth can be added later via get_current_user).
"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.video import Video
from app.models.moderation import ModerationReport

router = APIRouter(prefix="/admin", tags=["Admin"])


# ─────────────────────────────────────────────────────────────────────────────
# Inline serialisers
# ─────────────────────────────────────────────────────────────────────────────

def _user_dict(u: User) -> Dict[str, Any]:
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email or "",
        "role": "ADMIN" if (u.email or "").endswith("@echoreels.in") else "USER",
        "language": "bho",
        "status": "active",
        "watchMinutes": 0,
        "createdAt": datetime.utcnow().strftime("%Y-%m-%d"),
    }


def _video_dict(v: Video) -> Dict[str, Any]:
    return {
        "id": v.id,
        "title": v.title,
        "vertical": v.vertical or "entertainment",
        "language": v.language or "bho",
        "kind": "episode",
        "status": v.status or "published",
        "mature": v.is_18_plus or False,
        "durationSec": v.duration or 120,
        "episodes": v.total_episodes or 1,
        "views": v.views or 0,
        "likes": v.likes or 0,
        "rating": 4.5,
        "creatorId": v.creator_id,
        "creatorName": v.creator_name or "Unknown",
        "createdAt": v.created_at.strftime("%Y-%m-%d") if v.created_at else datetime.utcnow().strftime("%Y-%m-%d"),
        "publishedAt": v.created_at.strftime("%Y-%m-%d") if v.created_at and (v.status or "published") == "published" else None,
    }


def _report_dict(r: ModerationReport) -> Dict[str, Any]:
    return {
        "id": r.id,
        "videoId": r.video_id,
        "videoTitle": r.video_title,
        "reason": r.reason,
        "reports": r.reports_count,
        "status": r.status,
        "note": r.note,
        "reportedAt": r.reported_at.strftime("%Y-%m-%d") if r.reported_at else datetime.utcnow().strftime("%Y-%m-%d"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# FIX 3 — Dashboard Stats with real views trend from DB
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_videos = db.query(func.count(Video.id)).scalar() or 0
    published_videos = db.query(func.count(Video.id)).filter(Video.status == "published").scalar() or 0
    processing_videos = db.query(func.count(Video.id)).filter(Video.status == "processing").scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_creators = db.query(func.count(func.distinct(Video.creator_id))).scalar() or 0
    total_views = db.query(func.sum(Video.views)).scalar() or 0
    watch_hours = int(total_views * 2 / 60)
    pending_reports = db.query(func.count(ModerationReport.id)).filter(ModerationReport.status == "pending").scalar() or 0

    # Real views trend: group videos by created_at date for last 7 days
    today = datetime.utcnow().date()
    day_labels = {
        (today - timedelta(days=i)).strftime("%Y-%m-%d"): (today - timedelta(days=i)).strftime("%a")
        for i in range(6, -1, -1)
    }

    # Sum views of videos created each day (best proxy when no view_events table)
    rows = (
        db.query(
            cast(Video.created_at, Date).label("day"),
            func.sum(Video.views).label("views"),
        )
        .filter(Video.created_at >= datetime.utcnow() - timedelta(days=7))
        .group_by(cast(Video.created_at, Date))
        .all()
    )
    day_views = {str(r.day): (r.views or 0) for r in rows}

    views_trend = [
        {"day": label, "views": day_views.get(date_str, 0)}
        for date_str, label in day_labels.items()
    ]

    # Vertical mix from DB
    vertical_counts = (
        db.query(Video.vertical, func.sum(Video.views))
        .group_by(Video.vertical)
        .all()
    )
    vertical_mix = [
        {"vertical": (vc[0] or "other").capitalize(), "views": vc[1] or 0}
        for vc in vertical_counts
        if vc[0]
    ]
    if not vertical_mix:
        vertical_mix = [{"vertical": "Entertainment", "views": total_views}]

    return {
        "totalVideos": total_videos,
        "publishedVideos": published_videos,
        "processingVideos": processing_videos,
        "totalCreators": total_creators,
        "totalUsers": total_users,
        "watchHours": watch_hours,
        "pendingReports": pending_reports,
        "viewsTrend": views_trend,
        "verticalMix": vertical_mix,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Videos
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/videos")
def list_admin_videos(
    page: int = Query(1, ge=1),
    pageSize: int = Query(8, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    vertical: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Video)
    if search:
        q = q.filter(Video.title.ilike(f"%{search}%"))
    if status and status != "all":
        q = q.filter(Video.status == status)
    if vertical and vertical != "all":
        q = q.filter(Video.vertical == vertical)
    if language and language != "all":
        q = q.filter(Video.language == language)

    total = q.count()
    items = q.order_by(Video.created_at.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    return {"items": [_video_dict(v) for v in items], "total": total, "page": page, "pageSize": pageSize}


@router.get("/videos/{video_id}")
def get_admin_video(video_id: str, db: Session = Depends(get_db)):
    v = db.query(Video).filter(Video.id == video_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")
    return _video_dict(v)


@router.post("/videos")
def create_admin_video(payload: dict, db: Session = Depends(get_db)):
    video = Video(
        id=str(uuid.uuid4()),
        title=payload.get("title", "Untitled"),
        description=payload.get("description", ""),
        video_url=payload.get("videoUrl", ""),
        thumbnail_url=payload.get("thumbnailUrl", ""),
        duration=payload.get("durationSec", 120),
        creator_id=payload.get("creatorId", "admin"),
        creator_name=payload.get("creatorName", "Admin"),
        creator_username=payload.get("creatorUsername", "admin"),
        category_id=payload.get("vertical", "entertainment"),
        category_name=payload.get("vertical", "entertainment").capitalize(),
        language=payload.get("language", "भोजपुरी"),
        vertical=payload.get("vertical", "entertainment"),
        is_18_plus=payload.get("mature", False),
        status=payload.get("status", "draft"),
        total_episodes=payload.get("episodes", 1),
        badge=payload.get("badge"),
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return _video_dict(video)


@router.patch("/videos/{video_id}")
def update_admin_video(video_id: str, payload: dict, db: Session = Depends(get_db)):
    v = db.query(Video).filter(Video.id == video_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")
    if "status" in payload:
        v.status = payload["status"]
    if "title" in payload:
        v.title = payload["title"]
    if "vertical" in payload:
        v.vertical = payload["vertical"]
    if "mature" in payload:
        v.is_18_plus = payload["mature"]
    db.commit()
    db.refresh(v)
    return _video_dict(v)


@router.delete("/videos/{video_id}")
def delete_admin_video(video_id: str, db: Session = Depends(get_db)):
    v = db.query(Video).filter(Video.id == video_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")
    db.delete(v)
    db.commit()
    return {"deleted": video_id}


# ─────────────────────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/users")
def list_admin_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.name).all()
    return [_user_dict(u) for u in users]


@router.patch("/users/{user_id}")
def update_admin_user(user_id: str, payload: dict, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if "name" in payload:
        u.name = payload["name"]
    if "email" in payload:
        u.email = payload["email"]
    db.commit()
    db.refresh(u)
    return _user_dict(u)


# ─────────────────────────────────────────────────────────────────────────────
# FIX 2 — Creators with persisted `verified` in User table
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/creators")
def list_creators(db: Session = Depends(get_db)):
    rows = (
        db.query(
            Video.creator_id,
            Video.creator_name,
            Video.creator_username,
            Video.creator_avatar,
            func.count(Video.id).label("video_count"),
            func.sum(Video.views).label("total_views"),
        )
        .group_by(
            Video.creator_id,
            Video.creator_name,
            Video.creator_username,
            Video.creator_avatar,
        )
        .all()
    )
    # Look up verified status from users table
    user_ids = [r.creator_id for r in rows]
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()}

    return [
        {
            "id": r.creator_id,
            "name": r.creator_name or "Unknown",
            "handle": r.creator_username or r.creator_id,
            "language": "bho",
            "verified": users_map.get(r.creator_id, User()).verified or False,
            "followers": users_map.get(r.creator_id, User()).followers or 0,
            "videoCount": r.video_count or 0,
            "totalViews": r.total_views or 0,
            "joinedAt": datetime.utcnow().strftime("%Y-%m-%d"),
        }
        for r in rows
    ]


@router.patch("/creators/{creator_id}")
def update_creator(creator_id: str, payload: dict, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == creator_id).first()
    if u and "verified" in payload:
        u.verified = payload["verified"]
        db.commit()

    video_count = db.query(func.count(Video.id)).filter(Video.creator_id == creator_id).scalar() or 0
    return {
        "id": creator_id,
        "name": u.name if u else creator_id,
        "handle": u.username if u else creator_id,
        "language": "bho",
        "verified": u.verified if u else payload.get("verified", False),
        "followers": u.followers if u else 0,
        "videoCount": video_count,
        "joinedAt": datetime.utcnow().strftime("%Y-%m-%d"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Categories
# ─────────────────────────────────────────────────────────────────────────────

_CATEGORY_VERTICALS = [
    {"slug": "entertainment", "label": "Entertainment", "emoji": "🎭", "mature": False},
    {"slug": "movies",        "label": "Movies",        "emoji": "🎬", "mature": False},
    {"slug": "comedy",        "label": "Comedy",        "emoji": "😂", "mature": False},
    {"slug": "songs",         "label": "Songs",         "emoji": "🎵", "mature": False},
    {"slug": "shorts",        "label": "Shorts",        "emoji": "⚡", "mature": False},
    {"slug": "news",          "label": "News",          "emoji": "📰", "mature": False},
    {"slug": "lifestyle",     "label": "Lifestyle",     "emoji": "🌿", "mature": False},
    {"slug": "interviews",    "label": "Interviews",    "emoji": "🎙️", "mature": False},
    {"slug": "culture",       "label": "Culture",       "emoji": "🪔", "mature": False},
    {"slug": "mature",        "label": "18+ Mature",    "emoji": "🔞", "mature": True},
]


@router.get("/categories")
def list_admin_categories(db: Session = Depends(get_db)):
    counts = dict(
        db.query(Video.vertical, func.count(Video.id))
        .group_by(Video.vertical)
        .all()
    )
    return [
        {
            "id": f"cat-{v['slug']}",
            "slug": v["slug"],
            "label": v["label"],
            "emoji": v["emoji"],
            "language": "bho",
            "mature": v["mature"],
            "featured": i < 4,
            "videoCount": counts.get(v["slug"], 0),
            "order": i + 1,
        }
        for i, v in enumerate(_CATEGORY_VERTICALS)
    ]


@router.patch("/categories/{category_id}")
def update_category(category_id: str, payload: dict, db: Session = Depends(get_db)):
    slug = category_id.replace("cat-", "")
    cat = next((v for v in _CATEGORY_VERTICALS if v["slug"] == slug), None)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    counts = dict(
        db.query(Video.vertical, func.count(Video.id))
        .group_by(Video.vertical)
        .all()
    )
    return {
        "id": category_id,
        "slug": slug,
        "label": payload.get("label", cat["label"]),
        "emoji": payload.get("emoji", cat["emoji"]),
        "language": "bho",
        "mature": cat["mature"],
        "featured": payload.get("featured", False),
        "videoCount": counts.get(slug, 0),
        "order": payload.get("order", 1),
    }


# ─────────────────────────────────────────────────────────────────────────────
# FIX 1 — Moderation Reports persisted in DB
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/reports")
def list_moderation_reports(db: Session = Depends(get_db)):
    reports = db.query(ModerationReport).order_by(ModerationReport.reported_at.desc()).all()
    return [_report_dict(r) for r in reports]


@router.post("/reports")
def create_report(payload: dict, db: Session = Depends(get_db)):
    """Called when a user reports a video from the app."""
    video_id = payload.get("videoId", "")
    video = db.query(Video).filter(Video.id == video_id).first()

    # If a report for this video already exists and is pending, increment count
    existing = (
        db.query(ModerationReport)
        .filter(ModerationReport.video_id == video_id, ModerationReport.status == "pending")
        .first()
    )
    if existing:
        existing.reports_count += 1
        db.commit()
        db.refresh(existing)
        return _report_dict(existing)

    report = ModerationReport(
        id=str(uuid.uuid4()),
        video_id=video_id,
        video_title=video.title if video else payload.get("videoTitle", "Unknown"),
        reason=payload.get("reason", "other"),
        reports_count=1,
        status="pending",
        note=payload.get("note"),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return _report_dict(report)


@router.patch("/reports/{report_id}")
def resolve_report(report_id: str, payload: dict, db: Session = Depends(get_db)):
    report = db.query(ModerationReport).filter(ModerationReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = payload.get("status", report.status)
    report.note = payload.get("note", report.note)
    report.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(report)
    return _report_dict(report)
