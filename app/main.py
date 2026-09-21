from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 — registers all ORM models with Base.metadata
from app.routers import auth, shows, videos, categories, comments, users, search, notifications, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only create tables — no dummy data seeding
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware for local frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(shows.router, prefix=settings.API_V1_STR)
app.include_router(videos.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(comments.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "status": "online",
        "platform": "Echo Reels Bhojpuri OTT API",
        "docs": "/docs",
        "version": settings.VERSION
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "bhojpuri-backend"}
