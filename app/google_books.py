import httpx
from .config import settings
from typing import List, Dict

BASE_URL = "https://www.googleapis.com/books/v1/volumes"

async def search_books_by_keywords(q: str, max_results: int = 20) -> List[Dict]:
    params = {"q": q, "maxResults": max_results}
    key = (settings.google_books_api_key or "").strip()
    # Only include key if it looks real (not placeholder or empty)
    if key and not key.startswith("<") and "replace_with" not in key.lower():
        params["key"] = key
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(BASE_URL, params=params)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError:
        return []
    items = data.get("items", [])
    return [normalize_book(item) for item in items]

def normalize_book(item: Dict) -> Dict:
    v = item.get("volumeInfo", {})
    return {
        "book_id": item.get("id"),
        "title": v.get("title"),
        "authors": v.get("authors", []),
        "publisher": v.get("publisher"),
        "publishedDate": v.get("publishedDate"),
        "description": v.get("description"),
        "categories": v.get("categories", []),  # genres
        "pageCount": v.get("pageCount"),
        "thumbnail": v.get("imageLinks", {}).get("thumbnail"),
        "infoLink": v.get("infoLink")
    }

async def search_books_by_genre(genre: str, max_results: int = 20):
    q = f"subject:{genre}"
    return await search_books_by_keywords(q, max_results)

async def search_books_by_author(author: str, max_results: int = 20):
    q = f"inauthor:{author}"
    return await search_books_by_keywords(q, max_results)
