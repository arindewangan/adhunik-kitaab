# Book Recommendation Engine

A modern web application that provides personalized book recommendations using machine learning algorithms and the Google Books API. Users can search for books, rate them, and receive tailored recommendations based on their preferences.

## Features

- **User Authentication**: Secure user registration, login, and password reset functionality
- **Book Search**: Search for books using the Google Books API
- **Rating System**: Interactive star rating system for books
- **Personalized Recommendations**: ML-powered recommendations based on user ratings and preferences
- **User Dashboard**: View and manage personal book ratings
- **Responsive Design**: Modern, mobile-friendly interface using Tailwind CSS

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: Flask, HTML5, Tailwind CSS, JavaScript
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Machine Learning**: Scikit-learn for recommendation algorithms
- **External APIs**: Google Books API
- **Authentication**: JWT tokens with secure session management
- **Containerization**: Docker for easy deployment

## Project Structure

```
Book Recommendation Engine/
├── app/
│   ├── auth.py              # Authentication logic
│   ├── config.py            # Configuration settings
│   ├── db.py                # Database models and connections
│   ├── frontend.py          # Flask frontend application
│   ├── google_books.py      # Google Books API integration
│   ├── main.py              # FastAPI backend application
│   ├── models.py            # Data models
│   ├── recommender.py       # ML recommendation engine
│   ├── static/
│   │   └── styles.css       # Custom CSS styles
│   └── templates/           # HTML templates
├── dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create from .env.example)
└── README.md               # This file
```

## Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- Google Books API key (optional, for enhanced book data)

## 🚀 Local Development

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Book Recommendation Engine"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the root directory:
   
   ```env
   # Database
   DATABASE_URL=sqlite:///./books.db
   
   # API Configuration
   API_PORT=8000
   FRONTEND_PORT=5001
   
   # Security
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   
   # Google Books API (optional)
   GOOGLE_BOOKS_API_KEY=your-google-books-api-key
   
   # Email Configuration (for password reset)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

5. **Initialize the database:**
   ```bash
   python -c "from app.db import init_db; init_db()"
   ```

6. **Run the application:**

   **Option A: Run both services separately (Recommended for development):**
   
   Terminal 1 - Backend API:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   
   Terminal 2 - Frontend:
   ```bash
   python -c "from app.frontend import create_flask_app; app = create_flask_app(); app.run(host='127.0.0.1', port=5001, debug=True)"
   ```
   
   **Option B: Run integrated application:**
   ```bash
   python -m app.frontend
   ```

7. **Access the application:**
   - Frontend: http://localhost:5001
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Docker Deployment

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t book-recommendation-engine .

# Run the container
docker run -p 8000:8000 -p 5001:5001 --env-file .env book-recommendation-engine
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## AWS EC2 Deployment

### 1. Launch EC2 Instance

- Choose Amazon Linux 2 or Ubuntu 20.04 LTS
- Instance type: t3.micro or larger
- Configure security group to allow:
  - SSH (port 22) from your IP
  - HTTP (port 80) from anywhere
  - HTTPS (port 443) from anywhere
  - Custom TCP (port 8000) from anywhere
  - Custom TCP (port 5001) from anywhere

### 2. Connect to EC2 Instance

```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

### 3. Install Docker

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 4. Deploy Application

```bash
# Clone repository
git clone <your-repository-url>
cd "Book Recommendation Engine"

# Create production environment file
sudo nano .env
# Add your production environment variables

# Build and run
docker-compose up -d
```

### 5. Configure Reverse Proxy (Optional)

For production, consider using Nginx as a reverse proxy:

```bash
# Install Nginx
sudo yum install -y nginx

# Configure Nginx (create /etc/nginx/conf.d/book-app.conf)
sudo nano /etc/nginx/conf.d/book-app.conf
```

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password with token

### Books & Ratings
- `GET /search` - Search books
- `POST /ratings` - Add/update book rating
- `DELETE /ratings/{book_id}` - Delete book rating
- `GET /ratings` - Get user ratings
- `GET /recommendations` - Get personalized recommendations

### Frontend Routes
- `/` - Homepage with featured books
- `/search` - Book search page
- `/my-ratings` - User ratings dashboard
- `/recommendations` - Personalized recommendations

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./books.db` |
| `API_PORT` | Backend API port | `8000` |
| `FRONTEND_PORT` | Frontend application port | `5001` |
| `SECRET_KEY` | Flask secret key | Required |
| `JWT_SECRET_KEY` | JWT signing key | Required |
| `GOOGLE_BOOKS_API_KEY` | Google Books API key | Optional |


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository.

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port numbers in the `.env` file
2. **Database connection errors**: Ensure the database URL is correct and the database is accessible
3. **API key errors**: Verify your Google Books API key is valid and has the necessary permissions
4. **Docker build fails**: Ensure Docker is running and you have sufficient disk space

### Logs

- Application logs: `docker-compose logs app`
- Database logs: Check your database server logs
- Nginx logs: `/var/log/nginx/error.log` and `/var/log/nginx/access.log`