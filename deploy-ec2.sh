#!/bin/bash

# kders.com Email Server - AWS EC2 Deployment Script
# This script sets up your email server on a fresh Ubuntu 22.04 EC2 instance

set -e  # Exit on any error

echo "================================================"
echo "kders.com Email Server - EC2 Deployment"
echo "================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - UPDATE THESE!
DOMAIN="kders.duckdns.org"  # Change to your DuckDNS subdomain (e.g., yourname.duckdns.org)
MAIL_SUBDOMAIN="kders.duckdns.org"  # Same as DOMAIN for DuckDNS
GITHUB_REPO="https://github.com/YOUR_USERNAME/kders-mail.git"  # Update this
BRANCH="cn"  # or "main" depending on your branch

# For Cloudflare users (if you have a paid domain):
# DOMAIN="kders.com"
# MAIL_SUBDOMAIN="mail.kders.com"

echo -e "${YELLOW}Step 1/8: Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo -e "${YELLOW}Step 2/8: Installing Docker...${NC}"
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc 2>/dev/null || true

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo -e "${YELLOW}Step 3/8: Installing Git and required tools...${NC}"
sudo apt-get install -y git certbot python3-certbot-nginx ufw fail2ban

echo -e "${YELLOW}Step 4/8: Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 25/tcp      # SMTP
sudo ufw allow 587/tcp     # SMTP Submission
sudo ufw allow 110/tcp     # POP3
sudo ufw allow 993/tcp     # IMAPS (if needed later)
sudo ufw allow 995/tcp     # POP3S (if needed later)
sudo ufw allow 3000/tcp    # Frontend dev server (can remove in production)
sudo ufw allow 8000/tcp    # Backend API (can remove if using nginx proxy)

echo -e "${YELLOW}Step 5/8: Cloning repository...${NC}"
cd /opt
sudo git clone $GITHUB_REPO kders-mail
cd kders-mail
sudo git checkout $BRANCH

echo -e "${YELLOW}Step 6/8: Setting up environment variables...${NC}"
sudo tee .env > /dev/null <<EOF
# Database Configuration
DATABASE_URL=postgresql+asyncpg://mailuser:$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)@db:5432/maildb
POSTGRES_USER=mailuser
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
POSTGRES_DB=maildb

# JWT Secret
JWT_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

# AI Settings (optional)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
OPENAI_CHAT_MODEL=gpt-4o-mini
PGVECTOR_ENABLED=false

# Email Domain
MAIL_DOMAIN=$DOMAIN
EOF

echo -e "${YELLOW}Step 7/8: Obtaining SSL certificates...${NC}"
echo "Waiting for DNS to propagate (this may take a few minutes)..."
sleep 10

# Stop any service using port 80
sudo systemctl stop apache2 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true

# Get SSL certificates
# For DuckDNS (single domain):
sudo certbot certonly --standalone --agree-tos --non-interactive \
  --email admin@$DOMAIN \
  -d $DOMAIN

# For Cloudflare (multiple domains):
# sudo certbot certonly --standalone --agree-tos --non-interactive \
#   --email admin@$DOMAIN \
#   -d $DOMAIN \
#   -d $MAIL_SUBDOMAIN \
#   -d www.$DOMAIN

echo -e "${YELLOW}Step 8/8: Starting services...${NC}"
cd /opt/kders-mail
sudo docker-compose -f docker-compose.prod.yml up -d

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Your kders.com email server is now running!"
echo ""
echo "Services:"
echo "  - Web UI:      http://$DOMAIN"
echo "  - Backend API: http://$DOMAIN:8000"
echo "  - SMTP:        $MAIL_SUBDOMAIN:25 (receiving) and :587 (sending)"
echo "  - POP3:        $MAIL_SUBDOMAIN:110"
echo ""
echo "Next steps:"
echo "  1. Configure Cloudflare DNS (see CLOUDFLARE_DNS.md)"
echo "  2. Test email sending: telnet $MAIL_SUBDOMAIN 25"
echo "  3. Access web UI at http://$DOMAIN:3000"
echo ""
echo "SSL Certificates:"
echo "  - Located at: /etc/letsencrypt/live/$DOMAIN/"
echo "  - Auto-renewal configured via certbot"
echo ""
echo -e "${YELLOW}Important: Configure SPF, DKIM, and DMARC records (see DNS_SETUP.md)${NC}"
echo ""
