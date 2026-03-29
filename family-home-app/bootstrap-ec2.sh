#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Family Home App — EC2 Bootstrap (Ubuntu)
#
# Run this script ON your EC2 instance:
#   curl -sL https://raw.githubusercontent.com/fodelaye26/Plants/claude/family-home-os-SkWmv/family-home-app/bootstrap-ec2.sh | bash
#
# Or copy-paste the whole thing into your terminal.
# ============================================================

echo ""
echo "========================================"
echo "  Family Home App — EC2 Setup"
echo "========================================"
echo ""

# --- Prompt for config ---
read -rp "Notion API Key: " NOTION_API_KEY
read -rp "S3 bucket name for assets (leave empty to skip): " AWS_S3_BUCKET

NOTION_TASKS_DB_ID="bfe5382f554c4e8492c1dd1e99a9a4cb"
NOTION_CHORES_DB_ID="27e93b58f22f8158b024ebaf7354a277"

# --- Step 1: Install system dependencies ---
echo ""
echo "==> Step 1/7: Installing system packages..."
sudo apt update -qq
sudo apt install -y python3 python3-pip python3-venv nginx git

# --- Step 2: Clone the repo ---
echo ""
echo "==> Step 2/7: Cloning repository..."
APP_DIR="$HOME/family-home-app"
if [ -d "$APP_DIR" ]; then
    echo "    Directory exists, pulling latest..."
    cd "$APP_DIR" && git pull origin claude/family-home-os-SkWmv
else
    git clone https://github.com/fodelaye26/Plants.git "$HOME/Plants-temp"
    cd "$HOME/Plants-temp" && git checkout claude/family-home-os-SkWmv
    cp -r family-home-app "$APP_DIR"
    rm -rf "$HOME/Plants-temp"
fi

# --- Step 3: Set up Python backend ---
echo ""
echo "==> Step 3/7: Setting up Python backend..."
cd "$APP_DIR/backend"

python3 -m venv venv
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# --- Step 4: Create .env ---
echo ""
echo "==> Step 4/7: Writing .env config..."
cat > .env << ENVEOF
NOTION_API_KEY=${NOTION_API_KEY}
NOTION_TASKS_DB_ID=${NOTION_TASKS_DB_ID}
NOTION_CHORES_DB_ID=${NOTION_CHORES_DB_ID}
DATABASE_URL=sqlite:///./family_home.db
SYNC_INTERVAL_MINUTES=5
APP_ENV=production
AWS_S3_BUCKET=${AWS_S3_BUCKET}
AWS_S3_REGION=us-east-1
ENVEOF

echo "    .env written."

# --- Step 5: Test the backend ---
echo ""
echo "==> Step 5/7: Testing backend startup..."
timeout 5 python3 -c "
from app.main import app
print('    Backend imports OK')
" || true

# --- Step 6: Install systemd service ---
echo ""
echo "==> Step 6/7: Setting up systemd service..."
CURRENT_USER=$(whoami)
VENV_PATH="$APP_DIR/backend/venv"

sudo tee /etc/systemd/system/family-home-api.service > /dev/null << SVCEOF
[Unit]
Description=Family Home App API
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${APP_DIR}/backend
Environment=PATH=${VENV_PATH}/bin:/usr/bin
ExecStart=${VENV_PATH}/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl enable family-home-api
sudo systemctl start family-home-api

echo "    Service started."

# --- Step 7: Set up nginx reverse proxy ---
echo ""
echo "==> Step 7/7: Configuring nginx..."
sudo tee /etc/nginx/sites-available/family-home-api > /dev/null << 'NGXEOF'
server {
    listen 80;
    server_name _;

    # API backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
    }

    # Root
    location / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGXEOF

# Enable the site
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/family-home-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# --- Get public IP ---
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "your-ec2-ip")

# --- Done! ---
echo ""
echo "========================================"
echo "  DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "  API:        http://${PUBLIC_IP}/api/"
echo "  API Docs:   http://${PUBLIC_IP}/docs"
echo "  Health:     http://${PUBLIC_IP}/health"
echo ""
echo "  Next steps:"
echo ""
echo "  1. Open port 80 in your EC2 Security Group:"
echo "     AWS Console → EC2 → Security Groups → Inbound Rules"
echo "     Add: Type=HTTP, Port=80, Source=0.0.0.0/0"
echo ""
echo "  2. Test Notion sync:"
echo "     curl -X POST http://${PUBLIC_IP}/api/sync/notion"
echo ""
echo "  3. View your tasks:"
echo "     curl http://${PUBLIC_IP}/api/tasks/"
echo ""
echo "  4. Add SSL (optional but recommended):"
echo "     sudo apt install certbot python3-certbot-nginx"
echo "     sudo certbot --nginx -d yourdomain.com"
echo ""
echo "  Service commands:"
echo "     sudo systemctl status family-home-api"
echo "     sudo journalctl -u family-home-api -f"
echo ""
echo "========================================"
