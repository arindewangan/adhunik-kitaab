# Adhunik Kitaab - Book Recommendation Engine

A modern web application that provides personalized book recommendations using a rule-based algorithm and the Google Books API. Users can search for books, rate them, and receive tailored recommendations based on their genre and author preferences.

## Features

- **User Authentication**: Secure user registration, login, and password reset functionality
- **Book Search**: Search for books using the Google Books API
- **Rating System**: Interactive star rating system for books
- **Personalized Recommendations**: Rule-based recommendations based on user genre and author preferences
- **User Dashboard**: View and manage personal book ratings
- **Responsive Design**: Modern, mobile-friendly interface using Tailwind CSS

## Technology Stack

- **Backend**: Python, FastAPI, Motor (MongoDB async driver)
- **Frontend**: Flask, HTML5, Tailwind CSS, JavaScript
- **Database**: MongoDB (cloud-based MongoDB Atlas)
- **Recommendation Engine**: Rule-based algorithm using genre/author matching
- **External APIs**: Google Books API
- **Authentication**: JWT tokens with secure session management

## Project Structure

```
Adhunik Kitaab/
├── app/
│   ├── auth.py              # Authentication logic
│   ├── config.py            # Configuration settings
│   ├── db.py                # MongoDB connection and operations
│   ├── frontend.py          # Flask frontend application
│   ├── google_books.py      # Google Books API integration
│   ├── main.py              # FastAPI backend application
│   ├── models.py            # Data models
│   ├── recommender.py       # Rule-based recommendation engine
│   ├── static/
│   │   └── styles.css       # Custom CSS styles
│   └── templates/           # HTML templates
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create from .env.example)
├── deploy-simple.sh         # Simple EC2 deployment script
├── simple-ec2-deploy.md   # Manual EC2 deployment guide
└── README.md               # This file
```

## Prerequisites

- Python 3.8+
- MongoDB Atlas account (free tier available)
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
   cd adhunik-kitaab
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
   # Application Configuration
   PORT=8000
   
   # MongoDB Configuration
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
   DB_NAME=book_reco
   
   # Security
   SECRET_KEY=your-secret-key-here
   
   # Google Books API (optional)
   GOOGLE_BOOKS_API_KEY=your-google-books-api-key
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

## Deployment

### Simple EC2 Deployment (Recommended)

For easy deployment to AWS EC2 without Docker, use the provided deployment script:

```bash
# Make script executable
chmod +x deploy-simple.sh

# Run deployment script
./deploy-simple.sh
```

Or follow the manual deployment guide in `simple-ec2-deploy.md`.

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

### 3. Install Python and Dependencies

```bash
# Update system
sudo yum update -y

# Install Python and pip
sudo yum install -y python3 python3-pip git

# Clone repository
git clone <your-repository-url>
cd adhunik-kitaab

# Install Python dependencies
pip3 install -r requirements.txt
```

### 4. Configure Environment

```bash
# Create production environment file
cp .env.example .env
# Edit .env with your production values
nano .env
```

### 5. Run Application

```bash
# Run the application
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or use screen to keep it running in background
screen -dmS bookapp python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
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
| `PORT` | Application port | `8000` |
| `MONGODB_URI` | MongoDB Atlas connection string | Required |
| `DB_NAME` | MongoDB database name | `book_reco` |
| `SECRET_KEY` | Application secret key | Required |
| `GOOGLE_BOOKS_API_KEY` | Google Books API key | Optional |


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository.

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port number in the `.env` file
2. **MongoDB connection errors**: Ensure your MongoDB Atlas connection string is correct and IP is whitelisted
3. **API key errors**: Verify your Google Books API key is valid and has the necessary permissions
4. **Application not starting**: Check Python dependencies are installed and environment variables are set

### Logs

- Application logs: Check terminal output or use `screen -r bookapp` if running in background
- MongoDB logs: Check MongoDB Atlas dashboard for connection issues