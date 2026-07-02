#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   1. Get a VPS (cheapest options below)
#   2. Install Docker on it: curl -fsSL https://get.docker.com | sh
#   3. Run this script from your local machine
#
# Cheapest VPS options (2026):
#   Hetzner CX22   €3.29/mo  — https://hetzner.com
#   DigitalOcean   $6/mo     — https://digitalocean.com
#   Linode         $5/mo     — https://linode.com
#   Oracle Cloud   FREE      — https://oracle.com/cloud/free
#   AWS EC2 t2.micro FREE for 1yr — https://aws.amazon.com/ec2

if [ $# -lt 1 ]; then
    echo "Usage: $0 <user@vps-ip>"
    echo "  export COIN_DCX_API_KEY='your_key'"
    echo "  export COIN_DCX_API_SECRET='your_secret'"
    echo "  export DASHBOARD_USERNAME='admin'"
    echo "  export DASHBOARD_PASSWORD='your_password'"
    exit 1
fi

VPS="$1"
DIR="coindcx-bot"
ARCHIVE="/tmp/coindcx-bot-deploy.tar.gz"

echo "=== Packaging bot ==="
cd "$(dirname "$0")/.."
tar czf "$ARCHIVE" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='logs' \
    --exclude='.env' \
    "$DIR"

echo "=== Copying to VPS ($VPS) ==="
scp "$ARCHIVE" "$VPS:/tmp/"
ssh "$VPS" "tar xzf /tmp/coindcx-bot-deploy.tar.gz -C /opt && rm /tmp/coindcx-bot-deploy.tar.gz"
rm "$ARCHIVE"

echo "=== Setting up .env ==="
ssh "$VPS" "cat > /opt/$DIR/.env << EOF
COIN_DCX_API_KEY=${COIN_DCX_API_KEY:-}
COIN_DCX_API_SECRET=${COIN_DCX_API_SECRET:-}
DASHBOARD_USERNAME=${DASHBOARD_USERNAME:-admin}
DASHBOARD_PASSWORD=${DASHBOARD_PASSWORD:-admin}
BOT_MODE=paper
EOF"

echo "=== Starting bot via Docker ==="
ssh "$VPS" "cd /opt/$DIR && docker-compose up -d --build"

echo "=== Done ==="
echo "Dashboard:  http://$VPS:8501"
echo "Logs:       ssh $VPS 'docker logs -f coindcx-bot_dashboard_1'"
echo "Bot logs:   ssh $VPS 'docker logs -f coindcx-bot_bot_1'"
echo ""
echo "To enable live trading:"
echo "  1. ssh $VPS"
echo "  2. nano /opt/$DIR/config/config.json  # set auto_trade: true"
echo "  3. Set COIN_DCX_API_KEY/SECRET in /opt/$DIR/.env"
echo "  4. docker-compose restart"
echo ""
echo "For 24/7 uptime, most VPS providers include auto-reboot. Your bot resumes automatically."
