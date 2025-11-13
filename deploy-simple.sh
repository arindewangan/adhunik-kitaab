#!/bin/bash
# Simple EC2 Deployment Script - No Docker

echo "🚀 Starting simple EC2 deployment..."

# Update system
echo "📦 Updating system..."
sudo apt update -y

# Install Python and MongoDB
echo "🐍 Installing Python and MongoDB..."
sudo apt install python3-pip python3-venv mongodb -y
sudo systemctl start mongodb
sudo systemctl enable mongodb

# Install Python packages
echo "📚 Installing Python packages..."
pip3 install fastapi uvicorn motor pymongo python-dotenv requests flask python-jose passlib

# Create app directory
echo "📁 Creating app directory..."
mkdir -p ~/book-app
cd ~/book-app

# Create simple .env file
echo "⚙️  Creating environment file..."
cat > .env << EOF
PORT=8000
MONGODB_URI=mongodb://localhost:27017
DB_NAME=book_reco
GOOGLE_BOOKS_API_KEY=your_google_books_api_key_here
SECRET_KEY=$(openssl rand -hex 32)
EOF

echo "✅ Environment file created with random secret key"

# Create startup script
echo "📝 Creating startup script..."
cat > start-app.sh << 'EOF'
#!/bin/bash
cd ~/book-app
echo "Starting Book Recommendation App..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
EOF

chmod +x start-app.sh

# Install screen for background running
echo "🖥️  Installing screen..."
sudo apt install screen -y

# Create systemd service for auto-start
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/book-app.service > /dev/null << 'EOF'
[Unit]
Description=Book Recommendation App
After=network.target mongodb.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/book-app
ExecStart=/home/ubuntu/book-app/start-app.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable book-app.service

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Upload your app files to ~/book-app/"
echo "2. Run: ./start-app.sh (or use screen)"
echo "3. Or enable auto-start: sudo systemctl start book-app"
echo ""
echo "🌐 Your app will be available at: http://your-ec2-ip:8000"
echo "🔍 Check status: sudo systemctl status book-app"
echo "📜 View logs: journalctl -u book-app -f"