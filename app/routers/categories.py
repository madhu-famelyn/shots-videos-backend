from typing import List
from fastapi import APIRouter
from app.schemas.category import CategorySchema

router = APIRouter(prefix="/categories", tags=["Categories"])

CATEGORIES = [
    {"id": "trending", "name": "🔥 Trending", "slug": "trending"},
    {"id": "drama", "name": "🎭 Drama & Romance", "slug": "drama"},
    {"id": "18_plus", "name": "🔞 18+ Mature", "slug": "18-plus"},
    {"id": "short_serial", "name": "📺 Short Serials", "slug": "short-serial"},
    {"id": "thriller", "name": "⚡ Suspense & Thriller", "slug": "thriller"},
    {"id": "comedy", "name": "😂 Dehati Comedy", "slug": "comedy"},
]

@router.get("", response_model=List[CategorySchema])
def get_categories():
    return [CategorySchema(**c) for c in CATEGORIES]
