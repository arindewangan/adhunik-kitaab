# Simple EC2 Deployment (Free Tier) - No Docker

## What You Need
- AWS Account (Free Tier eligible)
- Your application files
- 15 minutes

## Step 1: Launch Free EC2 Instance

1. **Go to AWS Console** → EC2 → Launch Instance
2. **Choose these FREE options**:
   - **Name**: `book-app`
   - **Application**: Ubuntu Server 22.04 LTS
   - **Architecture**: 64-bit (x86)
   - **Instance type**: `t2.micro` (Free tier eligible)
   - **Key pair**: Create new (download .pem file)
   - **Network settings**: 
     - Allow SSH from anywhere
     - Allow HTTP from anywhere
     - Allow HTTPS from anywhere
   - **Storage**: 8GB (Free tier)

3. **Click Launch** (should show "Free tier eligible")

## Step 2: Connect to Your Instance

**Windows**: Use PuTTY
1. Convert .pem to .ppk using PuTTYgen
2. Connect with PuTTY: `ubuntu@your-ec2-ip`

**Mac/Linux**:
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

## Step 3: Install Everything in 5 Commands

```bash
# 1. Update system
sudo apt update -y

# 2. Install Python & MongoDB
sudo apt install python3-pip python3-venv mongodb -y
sudo systemctl start mongodb

# 3. Install Python packages
pip3 install fastapi uvicorn motor pymongo python-dotenv requests flask python-jose passlib

# 4. Create app directory
mkdir app && cd app
```

## Step 4: Upload Your Files

**Option A - Simple copy/paste**:
```bash
# On your EC2 instance, create files one by one
nano app.py  # Copy your main.py content
nano requirements.txt  # Copy from your local file
# etc...
```

**Option B - Use SCP (from your computer)**:
```bash
# Copy entire project
scp -i your-key.pem -r d:\adhunik-kitaab\* ubuntu@your-ec2-ip:~/app/
```

## Step 5: Configure Environment

```bash
# Create .env file
nano .env
```

Add this content:
```
PORT=8000
MONGODB_URI=mongodb://localhost:27017
DB_NAME=book_reco
GOOGLE_BOOKS_API_KEY=your_google_key_here
SECRET_KEY=make_this_random_string
```

## Step 6: Run Your App

```bash
# Start your app
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Test it**: Go to `http://your-ec2-ip:8000` in browser

## Step 7: Keep It Running (Simple Background)

```bash
# Install screen
sudo apt install screen -y

# Create new screen
screen -S bookapp

# Run your app
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Detach from screen: Ctrl+A, then D
# To reattach: screen -r bookapp
```

## Step 8: Free Domain (Optional)

Get a free domain at `yourname.pythonanywhere.com` or use your EC2 IP directly.

## Total Cost: $0

**What's Free:**
- EC2 t2.micro instance (750 hours/month for 12 months)
- 8GB storage
- Data transfer (up to 15GB)
- MongoDB (self-hosted)

## Quick Commands Reference

```bash
# Check if app is running
curl http://localhost:8000/health

# View logs
screen -r bookapp

# Stop app
Ctrl+C in screen session

# Restart app
detach (Ctrl+A, D) then reattach (screen -r bookapp)

# Check MongoDB
mongo
show dbs
```

## Troubleshooting

**App won't start?**
- Check MongoDB: `sudo systemctl status mongodb`
- Check port: `netstat -tlnp | grep 8000`
- Check logs in screen session

**Can't connect from browser?**
- Check AWS security groups (ports 80, 443, 8000)
- Check if app is running: `curl localhost:8000`

**MongoDB issues?**
- Restart: `sudo systemctl restart mongodb`
- Check status: `sudo systemctl status mongodb`

## That's It!

Your book recommendation app is now running on AWS EC2 for free. Just remember to stop the instance when not in use to preserve your free tier hours.