from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.seed import seed_database
from app.routers import auth, shows, videos, categories, comments, users, search, notifications

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed database on launch
    seed_database()
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
