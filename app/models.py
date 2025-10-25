from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RatingIn(BaseModel):
    user_id: Optional[str] = None
    book_id: str  # google books id
    rating: float = Field(..., ge=0.5, le=5.0)
    timestamp: Optional[datetime] = None
    # Book metadata (optional, stored for convenience)
    title: Optional[str] = None
    authors: Optional[List[str]] = []
    categories: Optional[List[str]] = []
    thumbnail: Optional[str] = None
    infoLink: Optional[str] = None
    publisher: Optional[str] = None
    publishedDate: Optional[str] = None

class PreferenceIn(BaseModel):
    user_id: str
    favorite_genres: Optional[List[str]] = []
    favorite_authors: Optional[List[str]] = []

class User(BaseModel):
    user_id: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None
