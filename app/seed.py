import json
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models.show import Show
from app.models.video import Video
from app.models.user import User

VIDEO_SOURCES = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
]

BHOJPURI_SHOWS = [
    {
        "id": "trend-1",
        "title": "Litti Chokha & Love Stories",
        "synopsis": "Two college rivals from Patna & Ara clash at a famous highway dhaba, sparking a passionate romance that defies their family feud.",
        "cover_image": "http://localhost:8080/bhojpuri/bhojpuri_romance.jpg",
        "genre": "Bhojpuri Romance",
        "language": "भोजपुरी",
        "rating": 4.9,
        "total_episodes": 8,
        "director": "Ravi Kishan Productions",
        "featured": True,
        "section_category": "trending",
        "badge": "🔥 #1 Hit",
        "cast": [
            {"name": "Pawan Singh", "role": "Suraj", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop"},
            {"name": "Akshara Singh", "role": "Pooja", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop"},
        ],
        "episodes": [
            {"id": "t1-e1", "episode_number": 1, "title": "Dhaba Par Pehli Mulaqaat", "duration": 110, "thumbnail_url": "http://localhost:8080/bhojpuri/bhojpuri_romance.jpg", "video_url": VIDEO_SOURCES[0], "views": 420000, "claps": 38400},
            {"id": "t1-e2", "episode_number": 2, "title": "Patna Junction Ke Baad", "duration": 95, "thumbnail_url": "http://localhost:8080/bhojpuri/bhojpuri_romance.jpg", "video_url": VIDEO_SOURCES[1], "views": 310000, "claps": 26800},
        ],
    },
    {
        "id": "trend-2",
        "title": "The Mukhiya’s Secret Daughter",
        "synopsis": "A high-powered Mumbai corporate lawyer returns to her ancestral village in Bihar to claim her rightful seat as village Mukhiya.",
        "cover_image": "http://localhost:8080/bhojpuri/bhojpuri_action.jpg",
        "genre": "Political Drama",
        "language": "भोजपुरी",
        "rating": 4.8,
        "total_episodes": 12,
        "director": "Manoj Tiwari Creative",
        "featured": True,
        "section_category": "trending",
        "badge": "⚡ 6M+ Plays",
        "cast": [
            {"name": "Khesari Lal", "role": "Rudra", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop"}
        ],
        "episodes": [
            {"id": "t2-e1", "episode_number": 1, "title": "Panchayat Ke Faisla", "duration": 118, "thumbnail_url": "http://localhost:8080/bhojpuri/bhojpuri_action.jpg", "video_url": VIDEO_SOURCES[2], "views": 510000, "claps": 42000},
        ],
    },
    {
        "id": "trend-3",
        "title": "Bhojpur College No. 1",
        "synopsis": "Four small-town boys start a viral Bhojpuri comedy podcast from their college terrace and become overnight superstars.",
        "cover_image": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&h=900&fit=crop",
        "genre": "Campus Comedy",
        "language": "भोजपुरी",
        "rating": 4.9,
        "total_episodes": 10,
        "director": "Pradeep Pandey",
        "section_category": "trending",
        "badge": "⭐ Bhojpuri Viral",
        "cast": [{"name": "Dinesh Lal Nirahua", "role": "Banti", "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&h=100&fit=crop"}],
        "episodes": [{"id": "t3-e1", "episode_number": 1, "title": "Mic On, Bawaal Shuru", "duration": 105, "thumbnail_url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=400&h=600&fit=crop", "video_url": VIDEO_SOURCES[3], "views": 390000, "claps": 34000}],
    },
    {
        "id": "cs-1",
        "title": "Badla: Bhojpur Ke Baaghi",
        "synopsis": "An honest train ticket examiner in Chapra takes on a local mafia syndicate to avenge his brother.",
        "cover_image": "http://localhost:8080/bhojpuri/bhojpuri_action.jpg",
        "genre": "Action & Revenge",
        "language": "भोजपुरी",
        "rating": 5.0,
        "total_episodes": 10,
        "director": "Yash Kumar",
        "is_coming_soon": True,
        "release_date": "Sept 15",
        "section_category": "coming_soon",
        "badge": "🔥 Mega Teaser",
        "cast": [{"name": "Pawan Singh", "role": "Vikram", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop"}],
        "episodes": [{"id": "cs1-e1", "episode_number": 1, "title": "Official Teaser Trailer", "duration": 45, "thumbnail_url": "http://localhost:8080/bhojpuri/bhojpuri_action.jpg", "video_url": VIDEO_SOURCES[0], "views": 750000, "claps": 62000}],
    },
    {
        "id": "18-1",
        "title": "Raat Ke Humsafar",
        "synopsis": "A married businesswoman in Gorakhpur gets trapped in a late-night forbidden affair with a charming guest.",
        "cover_image": "http://localhost:8080/bhojpuri/bhojpuri_romance.jpg",
        "genre": "18+ Romantic Suspense",
        "language": "भोजपुरी",
        "rating": 4.9,
        "total_episodes": 10,
        "director": "Karan Razdan",
        "is_18_plus": True,
        "section_category": "18_plus",
        "badge": "🔞 18+ Uncensored",
        "cast": [{"name": "Monalisa", "role": "Simran", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop"}],
        "episodes": [{"id": "18-1-e1", "episode_number": 1, "title": "Band Kamre Ka Raaz", "duration": 130, "thumbnail_url": "http://localhost:8080/bhojpuri/bhojpuri_romance.jpg", "video_url": VIDEO_SOURCES[4], "views": 680000, "claps": 48000}],
    }
]

REELS = [
    {
        "id": "v-1",
        "title": "Pawan Singh Grand Entry — Action Scene 🔥",
        "description": "Watch Pawan Singh's explosive power action entry in 2 minutes!",
        "video_url": VIDEO_SOURCES[0],
        "thumbnail_url": "http://localhost:8080/bhojpuri/bhojpuri_action.jpg",
        "duration": 110,
        "views": 485000,
        "likes": 42000,
        "comments_count": 1240,
        "creator_id": "c-1",
        "creator_name": "Pawan Singh",
        "creator_username": "pawansingh",
        "creator_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop",
        "category_id": "trending",
        "category_name": "🔥 Trending",
        "series_id": "trend-1",
        "series_title": "Litti Chokha & Love Stories",
        "episode_number": 1,
        "total_episodes": 8,
        "language": "भोजपुरी",
        "claps_count": 38400,
        "badge": "🔥 Top Reel"
    },
    {
        "id": "v-2",
        "title": "Khesari Lal Romance Twist ❤️",
        "description": "Passionate Bhojpuri dialogue and unforgettable 2-minute romance.",
        "video_url": VIDEO_SOURCES[1],
        "thumbnail_url": "http://localhost:8080/bhojpuri/bhojpuri_romance.jpg",
        "duration": 95,
        "views": 395000,
        "likes": 36500,
        "comments_count": 890,
        "creator_id": "c-2",
        "creator_name": "Khesari Lal Yadav",
        "creator_username": "khesari_official",
        "creator_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop",
        "category_id": "drama",
        "category_name": "🎭 Drama & Romance",
        "series_id": "trend-2",
        "series_title": "The Mukhiya’s Secret Daughter",
        "episode_number": 1,
        "total_episodes": 12,
        "language": "भोजपुरी",
        "claps_count": 42000,
        "badge": "⚡ Superhit"
    },
    {
        "id": "v-3",
        "title": "Nirahua Non-stop Comedy Dhamaal 😂",
        "description": "Hilarious village punchlines in 2-minute reel format.",
        "video_url": VIDEO_SOURCES[2],
        "thumbnail_url": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&h=900&fit=crop",
        "duration": 105,
        "views": 280000,
        "likes": 27400,
        "comments_count": 640,
        "creator_id": "c-3",
        "creator_name": "Dinesh Lal Nirahua",
        "creator_username": "nirahua_star",
        "creator_avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&h=100&fit=crop",
        "category_id": "trending",
        "category_name": "🔥 Trending",
        "series_id": "trend-3",
        "series_title": "Bhojpur College No. 1",
        "episode_number": 1,
        "total_episodes": 10,
        "language": "भोजपुरी",
        "claps_count": 34000,
        "badge": "⭐ Viral"
    }
]

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Show).count() == 0:
            for s in BHOJPURI_SHOWS:
                show = Show(
                    id=s["id"],
                    title=s["title"],
                    synopsis=s["synopsis"],
                    cover_image=s["cover_image"],
                    genre=s["genre"],
                    language=s.get("language", "भोजपुरी"),
                    rating=s.get("rating", 4.8),
                    total_episodes=s.get("total_episodes", 8),
                    director=s.get("director", "Bhojpuri Studios"),
                    featured=s.get("featured", False),
                    is_18_plus=s.get("is_18_plus", False),
                    is_coming_soon=s.get("is_coming_soon", False),
                    release_date=s.get("release_date"),
                    section_category=s.get("section_category", "trending"),
                    badge=s.get("badge"),
                    cast_json=json.dumps(s.get("cast", [])),
                    episodes_json=json.dumps(s.get("episodes", []))
                )
                db.add(show)
            db.commit()

        if db.query(Video).count() == 0:
            for r in REELS:
                video = Video(
                    id=r["id"],
                    title=r["title"],
                    description=r["description"],
                    video_url=r["video_url"],
                    thumbnail_url=r["thumbnail_url"],
                    duration=r["duration"],
                    views=r["views"],
                    likes=r["likes"],
                    comments_count=r["comments_count"],
                    creator_id=r["creator_id"],
                    creator_name=r["creator_name"],
                    creator_username=r["creator_username"],
                    creator_avatar=r["creator_avatar"],
                    category_id=r["category_id"],
                    category_name=r["category_name"],
                    series_id=r["series_id"],
                    series_title=r["series_title"],
                    episode_number=r["episode_number"],
                    total_episodes=r["total_episodes"],
                    language=r["language"],
                    claps_count=r["claps_count"],
                    badge=r.get("badge")
                )
                db.add(video)
            db.commit()

        if db.query(User).count() == 0:
            default_user = User(
                id="u_default_demo",
                phone="9876543210",
                email="viewer@echoreels.in",
                username="bhojpuri_star",
                name="Bhojpuri Superfan",
                bio="Dil Se Bhojpuri • Pawan Singh & Khesari Lal Fan 🎬",
                followers=480,
                following=12,
                total_likes=3200
            )
            db.add(default_user)
            db.commit()

        print("✅ Bhojpuri Database seeded successfully with shows, reels, and users!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
