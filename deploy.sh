#!/bin/bash

# Book Recommendation Engine Deployment Script
# This script helps deploy the application using Docker

set -e

echo "🚀 Book Recommendation Engine Deployment Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker Desktop."
        echo "On Windows: Start Docker Desktop from the Start menu"
        echo "On macOS: Start Docker Desktop from Applications"
        echo "On Linux: Run 'sudo systemctl start docker'"
        exit 1
    fi
    
    print_success "Docker is running"
}

# Build the Docker image
build_image() {
    print_status "Building Docker image..."
    
    if docker build -t book-recommendation-engine .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Run with docker-compose
run_with_compose() {
    print_status "Starting application with docker-compose..."
    
    if [ "$1" = "dev" ]; then
        print_status "Starting in development mode..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    elif [ "$1" = "prod" ]; then
        print_status "Starting in production mode..."
        docker-compose --profile production up -d
    else
        print_status "Starting in default mode..."
        docker-compose up -d
    fi
    
    print_success "Application started successfully"
    echo ""
    echo "🌐 Access the application at:"
    echo "   Frontend: http://localhost:5001"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
}

# Run standalone container
run_standalone() {
    print_status "Running standalone Docker container..."
    
    docker run -d \
        --name book-recommendation-engine \
        -p 8000:8000 \
        -p 5001:5001 \
        -v book_data:/app/data \
        -v book_logs:/app/logs \
        book-recommendation-engine
    
    print_success "Container started successfully"
    echo ""
    echo "🌐 Access the application at:"
    echo "   Frontend: http://localhost:5001"
    echo "   Backend API: http://localhost:8000"
}

# Stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop docker-compose services
    if docker-compose ps -q &> /dev/null; then
        docker-compose down
    fi
    
    # Stop standalone container
    if docker ps -q -f name=book-recommendation-engine &> /dev/null; then
        docker stop book-recommendation-engine
        docker rm book-recommendation-engine
    fi
    
    print_success "Services stopped"
}

# Show logs
show_logs() {
    if docker-compose ps -q &> /dev/null; then
        docker-compose logs -f
    elif docker ps -q -f name=book-recommendation-engine &> /dev/null; then
        docker logs -f book-recommendation-engine
    else
        print_warning "No running containers found"
    fi
}

# AWS EC2 deployment instructions
aws_deployment_help() {
    echo ""
    echo "🚀 AWS EC2 Deployment Instructions"
    echo "=================================="
    echo ""
    echo "1. Launch an EC2 instance:"
    echo "   - Choose Amazon Linux 2 or Ubuntu 20.04+ AMI"
    echo "   - Instance type: t3.small or larger"
    echo "   - Security group: Allow ports 22, 80, 443, 5001, 8000"
    echo ""
    echo "2. Connect to your EC2 instance:"
    echo "   ssh -i your-key.pem ec2-user@your-instance-ip"
    echo ""
    echo "3. Install Docker:"
    echo "   # Amazon Linux 2:"
    echo "   sudo yum update -y"
    echo "   sudo yum install -y docker"
    echo "   sudo systemctl start docker"
    echo "   sudo systemctl enable docker"
    echo "   sudo usermod -a -G docker ec2-user"
    echo ""
    echo "   # Ubuntu:"
    echo "   sudo apt update"
    echo "   sudo apt install -y docker.io docker-compose"
    echo "   sudo systemctl start docker"
    echo "   sudo systemctl enable docker"
    echo "   sudo usermod -a -G docker ubuntu"
    echo ""
    echo "4. Clone your repository:"
    echo "   git clone <your-repo-url>"
    echo "   cd book-recommendation-engine"
    echo ""
    echo "5. Deploy the application:"
    echo "   ./deploy.sh build"
    echo "   ./deploy.sh run"
    echo ""
    echo "6. Configure domain and SSL (optional):"
    echo "   - Point your domain to the EC2 instance IP"
    echo "   - Use Let's Encrypt for SSL certificates"
    echo "   - Update nginx.conf with your domain"
    echo ""
}

# Main script logic
case "$1" in
    "check")
        check_docker
        ;;
    "build")
        check_docker
        build_image
        ;;
    "run")
        check_docker
        run_with_compose "$2"
        ;;
    "standalone")
        check_docker
        build_image
        run_standalone
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "aws-help")
        aws_deployment_help
        ;;
    *)
        echo "Usage: $0 {check|build|run [dev|prod]|standalone|stop|logs|aws-help}"
        echo ""
        echo "Commands:"
        echo "  check      - Check if Docker is running"
        echo "  build      - Build the Docker image"
        echo "  run        - Run with docker-compose (default mode)"
        echo "  run dev    - Run in development mode"
        echo "  run prod   - Run in production mode with all services"
        echo "  standalone - Build and run as standalone container"
        echo "  stop       - Stop all services"
        echo "  logs       - Show application logs"
        echo "  aws-help   - Show AWS EC2 deployment instructions"
        echo ""
        echo "Examples:"
        echo "  $0 check"
        echo "  $0 build"
        echo "  $0 run"
        echo "  $0 run dev"
        echo "  $0 aws-help"
        exit 1
        ;;
esac