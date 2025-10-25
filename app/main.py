from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from .models import RatingIn, PreferenceIn, User
from .db import users_col, ratings_col, prefs_col
from .recommender import recommend_for_user, recommend_by_genre, recommend_by_author
from .google_books import search_books_by_keywords
from .config import settings
from typing import List
from starlette.middleware.wsgi import WSGIMiddleware
from .frontend import create_flask_app
from .auth import router as auth_router, get_current_user

app = FastAPI(title="Adhunik Kitaab")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Mount Flask frontend at /ui
app.mount("/ui", WSGIMiddleware(create_flask_app()))
# Include auth router
app.include_router(auth_router)

@app.on_event("startup")
async def startup():
    # create indexes for performance
    try:
        from .db import client
        # Test connection first
        await client.admin.command('ping')
        
        # Create indexes
        await users_col.create_index("user_id", unique=True)
        await users_col.create_index("email", unique=True)
        await ratings_col.create_index([("user_id", 1)])
        await ratings_col.create_index([("book_id", 1)])
        await prefs_col.create_index("user_id", unique=True)
        
        import logging
        logging.getLogger("startup").info("Database indexes created successfully")
    except Exception as e:
        import logging
        logging.getLogger("startup").warning(f"Skipping DB index creation: {e}")

@app.post("/users", status_code=201)
async def create_user(user: User):
    doc = user.dict()
    from datetime import datetime
    doc["created_at"] = datetime.utcnow()
    try:
        await users_col.insert_one(doc)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True, "user_id": user.user_id}

@app.post("/ratings", status_code=201)
async def add_rating(r: RatingIn, user=Depends(get_current_user)):
    # Override user_id from token
    doc = r.dict()
    doc["user_id"] = user["user_id"]
    doc["timestamp"] = doc.get("timestamp") or __import__("datetime").datetime.utcnow()
    await ratings_col.update_one(
        {"user_id": doc["user_id"], "book_id": doc["book_id"]},
        {"$set": doc},
        upsert=True,
    )
    return {"ok": True}

@app.get("/ratings/me")
async def get_my_ratings(user=Depends(get_current_user)):
    """Get all ratings for the current user with book details"""
    cursor = ratings_col.find({"user_id": user["user_id"]}).sort("timestamp", -1)
    ratings = []
    async for rating in cursor:
        # Include all rating data including book metadata if available
        rating_data = {
            "book_id": rating.get("book_id"),
            "rating": rating.get("rating"),
            "timestamp": rating.get("timestamp"),
            "title": rating.get("title"),
            "authors": rating.get("authors", []),
            "categories": rating.get("categories", []),
            "thumbnail": rating.get("thumbnail"),
            "infoLink": rating.get("infoLink"),
            "publisher": rating.get("publisher"),
            "publishedDate": rating.get("publishedDate")
        }
        ratings.append(rating_data)
    return {"count": len(ratings), "ratings": ratings}

@app.delete("/ratings/{book_id}")
async def delete_rating(book_id: str, user=Depends(get_current_user)):
    """Delete a rating for a specific book"""
    result = await ratings_col.delete_one({"user_id": user["user_id"], "book_id": book_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"ok": True, "message": "Rating deleted successfully"}

@app.get("/recommend/me")
async def recommend_me(limit: int = 20, user=Depends(get_current_user)):
    items = await recommend_for_user(user["user_id"], limit=limit)
    return {"count": len(items), "items": items}

@app.post("/preferences", status_code=201)
async def set_preferences(p: PreferenceIn):
    await prefs_col.update_one({"user_id": p.user_id}, {"$set": p.dict()}, upsert=True)
    return {"ok": True}

@app.get("/search")
async def search(q: str, limit: int = 10):
    items = await search_books_by_keywords(q, max_results=limit)
    return {"count": len(items), "items": items}

@app.get("/recommend/user/{user_id}")
async def recommend_user(user_id: str, limit: int = 20):
    items = await recommend_for_user(user_id, limit=limit)
    return {"count": len(items), "items": items}

@app.get("/recommend/genre")
async def recommend_genre(genre: str, limit: int = 20):
    items = await recommend_by_genre(genre, limit=limit)
    return {"count": len(items), "items": items}

@app.get("/recommend/author")
async def recommend_author(author: str, limit: int = 20):
    items = await recommend_by_author(author, limit=limit)
    return {"count": len(items), "items": items}

@app.get("/health")
async def health_check():
    """Health check endpoint to verify MongoDB connectivity"""
    try:
        # Test database connection
        from .db import client, db
        await client.admin.command('ping')
        
        # Test collections access
        user_count = await users_col.count_documents({})
        rating_count = await ratings_col.count_documents({})
        
        return {
            "status": "healthy",
            "database": "connected",
            "collections": {
                "users": user_count,
                "ratings": rating_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
