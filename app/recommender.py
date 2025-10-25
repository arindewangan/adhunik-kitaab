from .db import ratings_col, prefs_col, users_col
from .google_books import search_books_by_author, search_books_by_genre
from typing import List, Dict
import asyncio
from collections import Counter, defaultdict
import math

async def get_user_top_genres_and_authors(user_id: str, top_n: int = 5):
    # Fetch ratings by user
    cursor = ratings_col.find({"user_id": user_id})
    genre_counts = Counter()
    author_counts = Counter()
    async for r in cursor:
        # r expected to contain book metadata snapshot (if saved) else just book_id -> then we would fetch details
        if "categories" in r and r["categories"]:
            for g in r["categories"]:
                genre_counts[g.lower()] += r.get("rating", 0)
        if "authors" in r and r["authors"]:
            for a in r["authors"]:
                author_counts[a.lower()] += r.get("rating", 0)
    top_genres = [g for g, _ in genre_counts.most_common(top_n)]
    top_authors = [a for a, _ in author_counts.most_common(top_n)]
    return top_genres, top_authors

async def recommend_for_user(user_id: str, limit: int = 20) -> List[Dict]:
    # 1) derive user's top genres & authors
    top_genres, top_authors = await get_user_top_genres_and_authors(user_id, top_n=3)

    # 2) get books for each genre/author (concurrently)
    tasks = []
    for g in top_genres:
        tasks.append(search_books_by_genre(g, max_results=10))
    for a in top_authors:
        tasks.append(search_books_by_author(a, max_results=10))
    # if user has no prefs, fallback to generic popular subjects
    if not tasks:
        tasks.append(search_books_by_genre("fiction", max_results=15))
        tasks.append(search_books_by_genre("nonfiction", max_results=15))

    results = await asyncio.gather(*tasks)
    flat = [b for sub in results for b in sub]

    # 3) score books: base score + boost if matches user's top genres/authors + penalize already rated books
    scored = {}
    rated_books_cursor = ratings_col.find({"user_id": user_id})
    rated_ids = set()
    async for r in rated_books_cursor:
        rated_ids.add(r["book_id"])

    for b in flat:
        bid = b["book_id"]
        if not bid:
            continue
        score = 1.0
        # genre match boost
        for g in top_genres:
            if any(g in (c or "").lower() for c in b.get("categories", [])):
                score += 2.0
        # author match boost
        for a in top_authors:
            if any(a in (auth or "").lower() for auth in b.get("authors", [])):
                score += 2.5
        # small boost for not already rated
        if bid not in rated_ids:
            score += 0.5
        # de-dup best version
        if bid not in scored or score > scored[bid]["score"]:
            scored[bid] = {"score": score, "book": b}

    # return top N sorted
    sorted_books = sorted(scored.values(), key=lambda x: x["score"], reverse=True)
    return [s["book"] for s in sorted_books[:limit]]

# Simple public API: recommend by genre or author without personalization
async def recommend_by_genre(genre: str, limit: int = 20):
    return await search_books_by_genre(genre, max_results=limit)

async def recommend_by_author(author: str, limit: int = 20):
    return await search_books_by_author(author, max_results=limit)
