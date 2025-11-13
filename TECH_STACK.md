# Tech Stack Overview

Adhunik Kitaab is a Python-based book recommendation web app with a FastAPI backend and a lightweight Flask UI, designed for simple EC2 deployment without Docker.

## Architecture & Technology Choices

### Backend API: **FastAPI** (`app/main.py`)
**Why FastAPI?**
- **High Performance**: Built on Starlette and Pydantic, FastAPI is one of the fastest Python web frameworks
- **Async Support**: Native async/await support for handling concurrent requests efficiently
- **Automatic API Documentation**: Auto-generates interactive Swagger UI at `/docs`
- **Type Safety**: Built-in type checking and validation with Pydantic
- **Modern Python**: Leverages Python 3.7+ type hints for better code quality

**What it's used for:**
- RESTful API endpoints for book recommendations
- User authentication and authorization
- Integration with MongoDB and Google Books API
- Handling rating system and user preferences

### Frontend UI: **Flask** (`app/frontend.py`)
**Why Flask?**
- **Lightweight & Simple**: Minimal boilerplate, perfect for a simple UI
- **Template Engine**: Built-in Jinja2 templating for dynamic HTML
- **Easy Integration**: Simple to integrate with FastAPI backend
- **Development Friendly**: Quick prototyping and easy debugging
- **Minimal Overhead**: Doesn't add unnecessary complexity

**What it's used for:**
- User interface for login, signup, and book browsing
- Displaying recommendations and search results
- User rating interface
- Simple, clean web pages without JavaScript complexity

### Database: **MongoDB** with **Motor** (`app/db.py`)
**Why MongoDB?**
- **Flexible Schema**: Perfect for evolving book data and user preferences
- **JSON-like Documents**: Natural fit for book metadata and user data
- **Scalable**: Handles growing user base and book collection
- **Free Tier**: MongoDB Atlas offers generous free tier (512MB storage)
- **Rich Queries**: Supports complex queries for recommendations
- **Cloud-Hosted**: No server maintenance with MongoDB Atlas

**Why Motor (Async Driver)?**
- **Non-blocking**: Async operations don't block the event loop
- **Performance**: Handles multiple database operations concurrently
- **FastAPI Integration**: Designed to work seamlessly with FastAPI's async nature

**What it's used for:**
- Storing user accounts and authentication data
- Saving book ratings and user preferences
- Caching book information from Google Books API
- Storing password reset tokens

### Authentication: **JWT** with **Passlib** (`app/auth.py`)
**Why JWT (JSON Web Tokens)?**
- **Stateless**: No server-side session storage needed
- **Secure**: Cryptographically signed tokens
- **Scalable**: Works well in distributed systems
- **Standard**: Industry-standard authentication method
- **Cross-domain**: Works across different services

**Why Passlib?**
- **Secure Hashing**: Industry-standard password hashing (bcrypt)
- **Future-proof**: Supports multiple hashing algorithms
- **Easy Integration**: Simple API for password operations

**What it's used for:**
- User login and registration
- Secure password storage
- Session management
- Password reset functionality

### External Data: **Google Books API** (`app/google_books.py`)
**Why Google Books API?**
- **Comprehensive**: Millions of books with detailed metadata
- **Free Tier**: Generous free usage limits
- **Rich Data**: Book covers, descriptions, ratings, genres
- **Reliable**: Google's infrastructure ensures high availability
- **No Maintenance**: No need to manage book database

**What it's used for:**
- Searching books by title, author, or keywords
- Fetching book details and covers
- Getting genre information for recommendations
- Populating book metadata

### Recommendation Engine: **Rule-Based Algorithm** (`app/recommender.py`)
**Why Rule-Based Instead of Machine Learning?**
- **Simplicity**: No complex ML models to train or maintain
- **Speed**: Instant recommendations without training time
- **Transparency**: Easy to understand why books are recommended
- **No Data Requirements**: Works with minimal user data
- **Reliability**: Consistent results without model drift

**How It Works:**
- Analyzes user's rated books to find preferred genres and authors
- Searches Google Books API for similar genres/authors
- Scores books based on genre/author matches and user ratings
- Filters out already-rated books
- Returns top-scoring recommendations

**What it's used for:**
- Personalized book recommendations based on user preferences
- Genre-based and author-based recommendations
- Fallback recommendations for new users

### Configuration: **Pydantic Settings** (`app/config.py`)
**Why Pydantic Settings?**
- **Type Safety**: Automatic validation of environment variables
- **Documentation**: Self-documenting configuration
- **Default Values**: Sensible defaults with override capability
- **Environment Integration**: Seamless .env file integration

**What it's used for:**
- Managing API keys and secrets
- Database connection configuration
- Application settings (ports, timeouts, etc.)
- Environment-specific configurations

## Key Endpoints & Features

### Core API Endpoints
- `GET /health` — Health check and database connectivity
- `GET /search` — Search books via Google Books API
- `GET /recommend/me` — Personalized recommendations (requires auth)
- `GET /recommend/genre` — Genre-based recommendations
- `GET /recommend/author` — Author-based recommendations

### Authentication Endpoints
- `POST /auth/signup` — User registration
- `POST /auth/login` — User login (returns JWT)
- `GET /auth/me` — Get current user info
- `POST /auth/forgot` — Request password reset
- `POST /auth/reset` — Reset password

### Frontend Routes (Flask)
- `/` — Homepage with recommendations
- `/login` — User login page
- `/signup` — User registration page
- `/search` — Book search interface
- `/my-ratings` — User's rated books
- `/forgot-password` — Password reset request

## Dependencies & Runtime

### Core Dependencies
```
fastapi          # Modern, fast web framework
uvicorn          # ASGI server for FastAPI
motor            # Async MongoDB driver
pymongo          # MongoDB Python driver
pydantic         # Data validation using Python type hints
python-dotenv    # Environment variable management
requests         # HTTP library for API calls
flask            # Lightweight web framework for UI
python-jose      # JWT implementation
passlib          # Password hashing library
```

### Why These Specific Versions?
- **FastAPI**: Latest stable for maximum performance and features
- **Motor**: Compatible with FastAPI's async architecture
- **Pydantic**: Built into FastAPI for seamless integration
- **Flask**: Lightweight version for minimal overhead
- **JWT**: Industry-standard for secure authentication

## Configuration

Environment variables (`.env` file):
```
PORT=8000                                    # API server port
MONGODB_URI=mongodb://localhost:27017       # MongoDB connection
DB_NAME=book_reco                           # Database name
SECRET_KEY=your-secret-key-here             # JWT signing key
GOOGLE_BOOKS_API_KEY=your-google-api-key    # Google Books API access
```

## Simple EC2 Deployment (No Docker)

### Why No Docker?
- **Simplicity**: Direct deployment without container complexity
- **Cost**: No Docker Hub fees or container registry costs
- **Control**: Full control over the environment
- **Learning**: Better understanding of the deployment process
- **Debugging**: Easier to troubleshoot issues

### Deployment Stack
- **OS**: Ubuntu 22.04 LTS (Free tier eligible)
- **Python**: Python 3.10+ with virtual environment
- **Database**: MongoDB (self-hosted or MongoDB Atlas free tier)
- **Web Server**: Direct Python execution with Uvicorn
- **Process Manager**: systemd service or simple screen session

### Deployment Steps (5 minutes)
1. Launch free EC2 instance (t2.micro)
2. Install Python and MongoDB
3. Install Python dependencies
4. Upload application files
5. Configure environment variables
6. Start the application

## Development vs Production

### Development (Local)
```bash
# Run backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Run frontend (separate terminal)
python -c "from app.frontend import create_flask_app; app = create_flask_app(); app.run(host='127.0.0.1', port=5001, debug=True)"
```

### Production (EC2)
```bash
# Systemd service for auto-start
sudo systemctl start book-app

# Or simple background process
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

## Security Considerations

### Authentication Security
- **JWT Tokens**: Secure, time-limited authentication
- **Password Hashing**: bcrypt with salt rounds
- **Rate Limiting**: Prevents brute force attacks
- **CORS**: Configured for specific origins

### Data Security
- **Environment Variables**: Sensitive data in .env (not in code)
- **Input Validation**: Pydantic models prevent injection attacks
- **MongoDB Security**: Authentication and network isolation
- **HTTPS Ready**: Easy SSL certificate integration

## Performance Optimizations

### FastAPI Optimizations
- **Async Database Queries**: Non-blocking database operations
- **Response Caching**: Efficient data retrieval
- **Connection Pooling**: Reusable database connections
- **Lazy Loading**: Data loaded only when needed

### Frontend Optimizations
- **Minimal JavaScript**: Server-side rendered pages
- **CSS Caching**: Static file optimization
- **Template Caching**: Compiled templates for speed
- **Lightweight**: Minimal dependencies

## Monitoring & Maintenance

### Health Monitoring
- **Health Endpoint**: `/health` checks database connectivity
- **Process Monitoring**: systemd service status
- **Log Files**: Application and error logging
- **Resource Usage**: CPU and memory monitoring

### Maintenance Tasks
- **Database Backups**: Regular MongoDB dumps
- **Log Rotation**: Prevent disk space issues
- **Security Updates**: Regular system updates
- **Performance Monitoring**: Response time tracking

## Cost Optimization

### Free Tier Benefits
- **EC2 t2.micro**: 750 hours/month for 12 months
- **MongoDB Atlas**: 512MB free tier
- **Google Books API**: 1,000 requests/day free
- **Bandwidth**: 15GB/month outbound

### Resource Optimization
- **Efficient Code**: Minimal resource usage
- **Database Indexing**: Optimized queries
- **Caching**: Reduced API calls
- **Lightweight Stack**: No unnecessary dependencies

---

**Total Stack Cost**: $0 (Free tier) to ~$5/month (production)

**Deployment Time**: 5-10 minutes

**Maintenance**: Minimal - just keep dependencies updated