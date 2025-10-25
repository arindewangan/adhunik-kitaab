# Book Recommendation Engine Deployment Script (PowerShell)
# This script helps deploy the application using Docker on Windows

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("check", "build", "run", "standalone", "stop", "logs", "aws-help")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod")]
    [string]$Mode = "default"
)

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

function Test-Docker {
    Write-Status "Checking Docker installation..."
    
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker command not found"
        }
        
        $dockerInfo = docker info 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Docker is not running. Please start Docker Desktop."
            Write-Host "Start Docker Desktop from the Start menu or system tray" -ForegroundColor $Colors.Yellow
            exit 1
        }
        
        Write-Success "Docker is running"
        Write-Host "Docker version: $dockerVersion" -ForegroundColor $Colors.White
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor $Colors.Yellow
        exit 1
    }
}

function Build-Image {
    Write-Status "Building Docker image..."
    
    try {
        docker build -t book-recommendation-engine .
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker image built successfully"
        } else {
            throw "Build failed"
        }
    }
    catch {
        Write-Error "Failed to build Docker image"
        exit 1
    }
}

function Start-WithCompose {
    param([string]$Mode)
    
    Write-Status "Starting application with docker-compose..."
    
    try {
        switch ($Mode) {
            "dev" {
                Write-Status "Starting in development mode..."
                docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
            }
            "prod" {
                Write-Status "Starting in production mode..."
                docker-compose --profile production up -d
            }
            default {
                Write-Status "Starting in default mode..."
                docker-compose up -d
            }
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Application started successfully"
            Write-Host ""
            Write-Host "🌐 Access the application at:" -ForegroundColor $Colors.Green
            Write-Host "   Frontend: http://localhost:5001" -ForegroundColor $Colors.White
            Write-Host "   Backend API: http://localhost:8000" -ForegroundColor $Colors.White
            Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor $Colors.White
        } else {
            throw "Failed to start services"
        }
    }
    catch {
        Write-Error "Failed to start application with docker-compose"
        exit 1
    }
}

function Start-Standalone {
    Write-Status "Running standalone Docker container..."
    
    try {
        docker run -d `
            --name book-recommendation-engine `
            -p 8000:8000 `
            -p 5001:5001 `
            -v book_data:/app/data `
            -v book_logs:/app/logs `
            book-recommendation-engine
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Container started successfully"
            Write-Host ""
            Write-Host "🌐 Access the application at:" -ForegroundColor $Colors.Green
            Write-Host "   Frontend: http://localhost:5001" -ForegroundColor $Colors.White
            Write-Host "   Backend API: http://localhost:8000" -ForegroundColor $Colors.White
        } else {
            throw "Failed to start container"
        }
    }
    catch {
        Write-Error "Failed to run standalone container"
        exit 1
    }
}

function Stop-Services {
    Write-Status "Stopping services..."
    
    # Stop docker-compose services
    try {
        $composeServices = docker-compose ps -q 2>$null
        if ($composeServices) {
            docker-compose down
        }
    }
    catch {
        # Ignore errors if docker-compose is not running
    }
    
    # Stop standalone container
    try {
        $standaloneContainer = docker ps -q -f name=book-recommendation-engine 2>$null
        if ($standaloneContainer) {
            docker stop book-recommendation-engine
            docker rm book-recommendation-engine
        }
    }
    catch {
        # Ignore errors if container is not running
    }
    
    Write-Success "Services stopped"
}

function Show-Logs {
    try {
        $composeServices = docker-compose ps -q 2>$null
        if ($composeServices) {
            docker-compose logs -f
        } else {
            $standaloneContainer = docker ps -q -f name=book-recommendation-engine 2>$null
            if ($standaloneContainer) {
                docker logs -f book-recommendation-engine
            } else {
                Write-Warning "No running containers found"
            }
        }
    }
    catch {
        Write-Warning "No running containers found"
    }
}

function Show-AWSHelp {
    Write-Host ""
    Write-Host "🚀 AWS EC2 Deployment Instructions" -ForegroundColor $Colors.Green
    Write-Host "==================================" -ForegroundColor $Colors.Green
    Write-Host ""
    Write-Host "1. Launch an EC2 instance:" -ForegroundColor $Colors.Yellow
    Write-Host "   - Choose Amazon Linux 2 or Ubuntu 20.04+ AMI"
    Write-Host "   - Instance type: t3.small or larger"
    Write-Host "   - Security group: Allow ports 22, 80, 443, 5001, 8000"
    Write-Host ""
    Write-Host "2. Connect to your EC2 instance:" -ForegroundColor $Colors.Yellow
    Write-Host "   ssh -i your-key.pem ec2-user@your-instance-ip"
    Write-Host ""
    Write-Host "3. Install Docker:" -ForegroundColor $Colors.Yellow
    Write-Host "   # Amazon Linux 2:"
    Write-Host "   sudo yum update -y"
    Write-Host "   sudo yum install -y docker"
    Write-Host "   sudo systemctl start docker"
    Write-Host "   sudo systemctl enable docker"
    Write-Host "   sudo usermod -a -G docker ec2-user"
    Write-Host ""
    Write-Host "   # Ubuntu:"
    Write-Host "   sudo apt update"
    Write-Host "   sudo apt install -y docker.io docker-compose"
    Write-Host "   sudo systemctl start docker"
    Write-Host "   sudo systemctl enable docker"
    Write-Host "   sudo usermod -a -G docker ubuntu"
    Write-Host ""
    Write-Host "4. Clone your repository:" -ForegroundColor $Colors.Yellow
    Write-Host "   git clone <your-repo-url>"
    Write-Host "   cd book-recommendation-engine"
    Write-Host ""
    Write-Host "5. Deploy the application:" -ForegroundColor $Colors.Yellow
    Write-Host "   chmod +x deploy.sh"
    Write-Host "   ./deploy.sh build"
    Write-Host "   ./deploy.sh run"
    Write-Host ""
    Write-Host "6. Configure domain and SSL (optional):" -ForegroundColor $Colors.Yellow
    Write-Host "   - Point your domain to the EC2 instance IP"
    Write-Host "   - Use Let's Encrypt for SSL certificates"
    Write-Host "   - Update nginx.conf with your domain"
    Write-Host ""
}

function Show-Help {
    Write-Host ""
    Write-Host "Book Recommendation Engine Deployment Script" -ForegroundColor $Colors.Green
    Write-Host "=============================================" -ForegroundColor $Colors.Green
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 -Action <action> [-Mode <mode>]" -ForegroundColor $Colors.Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor $Colors.Yellow
    Write-Host "  check      - Check if Docker is running"
    Write-Host "  build      - Build the Docker image"
    Write-Host "  run        - Run with docker-compose"
    Write-Host "  standalone - Build and run as standalone container"
    Write-Host "  stop       - Stop all services"
    Write-Host "  logs       - Show application logs"
    Write-Host "  aws-help   - Show AWS EC2 deployment instructions"
    Write-Host ""
    Write-Host "Modes (for run action):" -ForegroundColor $Colors.Yellow
    Write-Host "  dev        - Development mode with hot reload"
    Write-Host "  prod       - Production mode with all services"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $Colors.Yellow
    Write-Host "  .\deploy.ps1 -Action check"
    Write-Host "  .\deploy.ps1 -Action build"
    Write-Host "  .\deploy.ps1 -Action run"
    Write-Host "  .\deploy.ps1 -Action run -Mode dev"
    Write-Host "  .\deploy.ps1 -Action aws-help"
    Write-Host ""
    Write-Host "For local development without Docker:" -ForegroundColor $Colors.Yellow
    Write-Host ""
    Write-Host "Terminal 1 - Backend API:" -ForegroundColor $Colors.Blue
    Write-Host "  uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
    Write-Host ""
    Write-Host "Terminal 2 - Frontend:" -ForegroundColor $Colors.Blue
    Write-Host "  python -c `"from app.frontend import create_flask_app; app = create_flask_app(); app.run(host='127.0.0.1', port=5001, debug=True)`""
    Write-Host ""
}

# Main script logic
Write-Host ""
Write-Host "🚀 Book Recommendation Engine Deployment Script" -ForegroundColor $Colors.Green
Write-Host "================================================" -ForegroundColor $Colors.Green
Write-Host ""

switch ($Action) {
    "check" {
        Test-Docker
    }
    "build" {
        Test-Docker
        Build-Image
    }
    "run" {
        Test-Docker
        Start-WithCompose -Mode $Mode
    }
    "standalone" {
        Test-Docker
        Build-Image
        Start-Standalone
    }
    "stop" {
        Stop-Services
    }
    "logs" {
        Show-Logs
    }
    "aws-help" {
        Show-AWSHelp
    }
    default {
        Show-Help
    }
}