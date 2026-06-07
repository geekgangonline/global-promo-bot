#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Global Promo TV — VPS Setup Script
# Deploys the Telegram Operations Bot to a cloud server
# ─────────────────────────────────────────────────────────────
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  GPTV Operations Bot — VPS Installer${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 1. Check prerequisites
echo -e "\n${YELLOW}[1/6] Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    echo -e "${GREEN}Docker installed. You may need to log out/back in for group changes.${NC}"
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    sudo apt-get install -y docker-compose-plugin || sudo pip3 install docker-compose
fi

# 2. Clone/update code
echo -e "\n${YELLOW}[2/6] Setting up project...${NC}"
REPO_URL="${REPO_URL:-https://github.com/YOUR_USERNAME/gptv-bot.git}"

if [ -d "/opt/gptv-bot" ]; then
    echo "Updating existing installation..."
    cd /opt/gptv-bot
    git pull || true
else
    echo "Cloning fresh..."
    sudo git clone "$REPO_URL" /opt/gptv-bot
fi
cd /opt/gptv-bot

# 3. Create .env if not exists
echo -e "\n${YELLOW}[3/6] Setting up environment...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
# ─── TELEGRAM ──────────────────────────────────────────────
TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN=YOUR_TELEGRAM_ID
DEBUG=False

# ─── SESSION ───────────────────────────────────────────────
SESSION_DURATION=5 10 30

# ─── WHOP ──────────────────────────────────────────────────
WHOP_API_KEY=your_whop_api_key
WHOP_COMPANY_ID=your_whop_company_id

# ─── STAFF CHANNELS ────────────────────────────────────────
STAFF_CHAT_ID=
CREATOR_CHAT_ID=

# ─── OPENAI ───────────────────────────────────────────────
OPENAI_API_KEY=

# ─── GMAIL ────────────────────────────────────────────────
GMAIL_USER=
GMAIL_APP_PASSWORD=
ENVEOF
    echo -e "${YELLOW}.env file created. EDIT IT with your keys: nano /opt/gptv-bot/.env${NC}"
    echo -e "${YELLOW}Then re-run this script.${NC}"
    exit 1
fi

# 4. Build and start Docker
echo -e "\n${YELLOW}[4/6] Building Docker image...${NC}"
sudo docker compose build

echo -e "\n${YELLOW}[5/6] Starting bot...${NC}"
sudo docker compose up -d

# 5. Set up systemd for auto-restart (optional but recommended)
echo -e "\n${YELLOW}[6/6] Setting up auto-start...${NC}"
cat > /tmp/gptv-bot.service << 'SERVICEEOF'
[Unit]
Description=GPTV Operations Bot
Requires=docker.service
After=docker.service

[Service]
Restart=always
ExecStart=/usr/bin/docker compose -f /opt/gptv-bot/docker-compose.yml up
ExecStop=/usr/bin/docker compose -f /opt/gptv-bot/docker-compose.yml down
WorkingDirectory=/opt/gptv-bot

[Install]
WantedBy=multi-user.target
SERVICEEOF

sudo mv /tmp/gptv-bot.service /etc/systemd/system/gptv-bot.service
sudo systemctl daemon-reload
sudo systemctl enable gptv-bot.service

# 6. Check status
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\nBot status:"
sudo docker compose ps
echo -e "\nView logs:"
echo "  sudo docker compose logs -f"
echo -e "\nRestart bot:"
echo "  sudo systemctl restart gptv-bot"
echo -e "\nStop bot:"
echo "  sudo systemctl stop gptv-bot"
