from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

# We read settings at import time to get port and secret
from .config import settings

TEMPLATES_DIR = str(Path(__file__).parent / "templates")
STATIC_DIR = str(Path(__file__).parent / "static")

API_BASE = f"http://127.0.0.1:{settings.port}"

# Featured fallback items to display when API returns no data
SAMPLE_FEATURED = [
    {
        "book_id": "sample-1",
        "title": "The Pragmatic Programmer",
        "authors": ["Andrew Hunt", "David Thomas"],
        "categories": ["Software"],
        "thumbnail": None,
        "infoLink": "https://pragprog.com/titles/tpp20/the-pragmatic-programmer/",
    },
    {
        "book_id": "sample-2",
        "title": "Clean Code",
        "authors": ["Robert C. Martin"],
        "categories": ["Software"],
        "thumbnail": None,
        "infoLink": "https://www.informit.com/store/clean-code-a-handbook-of-agile-software-craftsmanship-9780132350884",
    },
    {
        "book_id": "sample-3",
        "title": "Atomic Habits",
        "authors": ["James Clear"],
        "categories": ["Self-help"],
        "thumbnail": None,
        "infoLink": "https://jamesclear.com/atomic-habits",
    },
    {
        "book_id": "sample-4",
        "title": "Sapiens: A Brief History of Humankind",
        "authors": ["Yuval Noah Harari"],
        "categories": ["History"],
        "thumbnail": None,
        "infoLink": "https://www.ynharari.com/book/sapiens/",
    },
    {
        "book_id": "sample-5",
        "title": "The Alchemist",
        "authors": ["Paulo Coelho"],
        "categories": ["Fiction"],
        "thumbnail": None,
        "infoLink": "https://paulocoelhoblog.com/the-alchemist/",
    },
    {
        "book_id": "sample-6",
        "title": "Thinking, Fast and Slow",
        "authors": ["Daniel Kahneman"],
        "categories": ["Psychology"],
        "thumbnail": None,
        "infoLink": "https://us.macmillan.com/books/9780374533557/thinkingfastandslow",
    },
]

def api_headers():
    token = session.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def merge_user_ratings_with_books(books):
    """Merge user ratings with book data for display"""
    if not session.get("token") or not books:
        return books
    
    try:
        # Fetch user's ratings
        r = requests.get(f"{API_BASE}/ratings/me", headers=api_headers(), timeout=12)
        r.raise_for_status()
        user_ratings = r.json().get("ratings", [])
        
        # Create a lookup dictionary for ratings by book_id
        ratings_lookup = {rating["book_id"]: rating["rating"] for rating in user_ratings}
        
        # Merge ratings with books
        for book in books:
            book_id = book.get("book_id")
            if book_id in ratings_lookup:
                book["user_rating"] = ratings_lookup[book_id]
            else:
                book["user_rating"] = None
                
        return books
    except Exception:
        # If fetching ratings fails, just return books without ratings
        return books


def create_flask_app() -> Flask:
    app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
    app.secret_key = settings.secret_key

    @app.get("/")
    def index():
        # Fetch recommended items automatically
        rec_items = []
        rec_error = None
        try:
            if session.get("token"):
                r = requests.get(f"{API_BASE}/recommend/me", params={"limit": 12}, headers=api_headers(), timeout=12)
            else:
                r = requests.get(f"{API_BASE}/recommend/genre", params={"genre": "fiction", "limit": 12}, timeout=12)
            r.raise_for_status()
            rec_items = r.json().get("items", [])
        except Exception as e:
            rec_error = str(e)
        # Fallback to featured items if empty
        if not rec_items:
            rec_items = SAMPLE_FEATURED
        
        # Merge user ratings with books
        rec_items = merge_user_ratings_with_books(rec_items)
        
        return render_template("index.html", user=session.get("user"), rec_items=rec_items, rec_error=rec_error)

    @app.get("/search")
    def search():
        q = request.args.get("q", "").strip()
        limit = int(request.args.get("limit", 12))
        items = []
        error = None
        if q:
            try:
                r = requests.get(f"{API_BASE}/search", params={"q": q, "limit": limit}, timeout=12)
                r.raise_for_status()
                data = r.json()
                items = data.get("items", [])
            except Exception as e:
                error = str(e)
        
        # Merge user ratings with search results
        items = merge_user_ratings_with_books(items)
        
        return render_template("results.html", title="Search Results", items=items, error=error, q=q, user=session.get("user"))

    @app.get("/recommend")
    def recommend():
        genre = request.args.get("genre", "").strip()
        author = request.args.get("author", "").strip()
        limit = int(request.args.get("limit", 20))
        items = []
        error = None
        try:
            if session.get("token") and not (genre or author):
                r = requests.get(f"{API_BASE}/recommend/me", params={"limit": limit}, headers=api_headers(), timeout=12)
            elif genre:
                r = requests.get(f"{API_BASE}/recommend/genre", params={"genre": genre, "limit": limit}, timeout=12)
            elif author:
                r = requests.get(f"{API_BASE}/recommend/author", params={"author": author, "limit": limit}, timeout=12)
            else:
                r = requests.get(f"{API_BASE}/recommend/genre", params={"genre": "fiction", "limit": limit}, timeout=12)
            r.raise_for_status()
            items = r.json().get("items", [])
        except Exception as e:
            error = str(e)
        
        # Merge user ratings with recommendation results
        items = merge_user_ratings_with_books(items)
        
        return render_template("results.html", title="Recommendations", items=items, error=error, user=session.get("user"))

    @app.post("/rate")
    def rate():
        form = request.form
        book_id = form.get("book_id", "").strip()
        rating = form.get("rating", "").strip()
        if not (book_id and rating):
            flash("Please select a rating.", "warning")
            return redirect(request.referrer or url_for("index"))
        try:
            # Include book metadata in the rating payload
            payload = {
                "book_id": book_id, 
                "rating": float(rating),
                "title": form.get("title", ""),
                "authors": form.get("authors", "").split(", ") if form.get("authors") else [],
                "categories": form.get("categories", "").split(", ") if form.get("categories") else [],
                "thumbnail": form.get("thumbnail", ""),
                "infoLink": form.get("infoLink", ""),
                "publisher": form.get("publisher", ""),
                "publishedDate": form.get("publishedDate", "")
            }
            r = requests.post(f"{API_BASE}/ratings", json=payload, headers=api_headers(), timeout=12)
            r.raise_for_status()
            flash("Rating saved!", "success")
        except Exception as e:
            flash(f"Failed to save rating: {e}", "error")
        return redirect(request.referrer or url_for("index"))

    @app.get("/my-ratings")
    def my_ratings():
        """Display user's ratings page"""
        if not session.get("token"):
            flash("Please log in to view your ratings.", "warning")
            return redirect(url_for("login_page"))
        
        ratings = []
        error = None
        try:
            r = requests.get(f"{API_BASE}/ratings/me", headers=api_headers(), timeout=12)
            r.raise_for_status()
            data = r.json()
            ratings = data.get("ratings", [])
        except Exception as e:
            error = f"Failed to load ratings: {e}"
        
        return render_template("my_ratings.html", title="My Ratings", ratings=ratings, error=error, user=session.get("user"))

    @app.post("/update-rating")
    def update_rating():
        """Update or delete a rating"""
        if not session.get("token"):
            flash("Please log in to update ratings.", "warning")
            return redirect(url_for("login_page"))
        
        form = request.form
        book_id = form.get("book_id", "").strip()
        action = form.get("action", "").strip()
        
        if not book_id:
            flash("Invalid book ID.", "error")
            return redirect(url_for("my_ratings"))
        
        try:
            if action == "delete":
                # Delete the rating (we'll need to add a delete endpoint)
                r = requests.delete(f"{API_BASE}/ratings/{book_id}", headers=api_headers(), timeout=12)
                r.raise_for_status()
                flash("Rating deleted successfully!", "success")
            else:
                # Update the rating
                rating = form.get("rating", "").strip()
                if not rating:
                    flash("Please select a rating.", "warning")
                    return redirect(url_for("my_ratings"))
                
                # Include book metadata in the rating payload
                payload = {
                    "book_id": book_id, 
                    "rating": float(rating),
                    "title": form.get("title", ""),
                    "authors": form.get("authors", "").split(", ") if form.get("authors") else [],
                    "categories": form.get("categories", "").split(", ") if form.get("categories") else [],
                    "thumbnail": form.get("thumbnail", ""),
                    "infoLink": form.get("infoLink", ""),
                    "publisher": form.get("publisher", ""),
                    "publishedDate": form.get("publishedDate", "")
                }
                r = requests.post(f"{API_BASE}/ratings", json=payload, headers=api_headers(), timeout=12)
                r.raise_for_status()
                flash("Rating updated successfully!", "success")
        except Exception as e:
            flash(f"Failed to update rating: {e}", "error")
        
        return redirect(url_for("my_ratings"))

    # Auth pages
    @app.get("/login")
    def login_page():
        return render_template("login.html", user=session.get("user"))

    @app.post("/login")
    def login_submit():
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        try:
            r = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password}, timeout=12)
            r.raise_for_status()
            data = r.json()
            session["token"] = data.get("token")
            session["user"] = data.get("user")
            flash("Welcome back!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Login failed: {e}", "error")
            return redirect(url_for("login_page"))

    @app.get("/signup")
    def signup_page():
        return render_template("signup.html", user=session.get("user"))

    @app.post("/signup")
    def signup_submit():
        name = request.form.get("name", "")
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        try:
            r = requests.post(f"{API_BASE}/auth/signup", json={"name": name, "email": email, "password": password}, timeout=12)
            r.raise_for_status()
            data = r.json()
            session["token"] = data.get("token")
            session["user"] = data.get("user")
            flash("Account created!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Signup failed: {e}", "error")
            return redirect(url_for("signup_page"))

    @app.get("/forgot")
    def forgot_page():
        return render_template("forgot.html", user=session.get("user"))

    @app.post("/forgot")
    def forgot_submit():
        email = request.form.get("email", "").strip()
        try:
            r = requests.post(f"{API_BASE}/auth/forgot", json={"email": email}, timeout=12)
            r.raise_for_status()
            data = r.json()
            flash(f"Reset token generated: {data.get('token')}", "success")
            return redirect(url_for("reset_page", token=data.get("token")))
        except Exception as e:
            flash(f"Failed to generate reset token: {e}", "error")
            return redirect(url_for("forgot_page"))

    @app.get("/reset")
    def reset_page():
        token = request.args.get("token", "")
        return render_template("reset.html", token=token, user=session.get("user"))

    @app.post("/reset")
    def reset_submit():
        token = request.form.get("token", "")
        new_password = request.form.get("new_password", "")
        try:
            r = requests.post(f"{API_BASE}/auth/reset", json={"token": token, "new_password": new_password}, timeout=12)
            r.raise_for_status()
            flash("Password reset successful. Please login.", "success")
            return redirect(url_for("login_page"))
        except Exception as e:
            flash(f"Failed to reset password: {e}", "error")
            return redirect(url_for("reset_page", token=token))

    @app.get("/logout")
    def logout():
        session.clear()
        flash("Logged out.", "success")
        return redirect(url_for("index"))

    return app