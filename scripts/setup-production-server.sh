#!/bin/bash
set -e

echo "================================================"
echo "Production Server Setup Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo -e "${RED}Please do not run this script as root${NC}"
  exit 1
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo -e "${GREEN}Step 2: Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}Docker installed successfully${NC}"
else
    echo -e "${YELLOW}Docker already installed${NC}"
fi

echo -e "${GREEN}Step 3: Installing Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    sudo apt-get install -y docker-compose-plugin
    echo -e "${GREEN}Docker Compose installed successfully${NC}"
else
    echo -e "${YELLOW}Docker Compose already installed${NC}"
fi

echo -e "${GREEN}Step 4: Adding user to docker group...${NC}"
sudo usermod -aG docker $USER

echo -e "${GREEN}Step 5: Installing additional tools...${NC}"
sudo apt-get install -y git curl wget nano

echo -e "${GREEN}Step 6: Creating deployment directory...${NC}"
DEPLOY_DIR="/opt/sogangcomputerclub.org"
if [ ! -d "$DEPLOY_DIR" ]; then
    sudo mkdir -p $DEPLOY_DIR
    sudo chown -R $USER:$USER $DEPLOY_DIR
    echo -e "${GREEN}Directory created: $DEPLOY_DIR${NC}"
else
    echo -e "${YELLOW}Directory already exists: $DEPLOY_DIR${NC}"
fi

echo -e "${GREEN}Step 7: Cloning repository...${NC}"
cd $DEPLOY_DIR
if [ ! -d ".git" ]; then
    read -p "Enter GitHub repository URL: " REPO_URL
    git clone $REPO_URL .
    echo -e "${GREEN}Repository cloned successfully${NC}"
else
    echo -e "${YELLOW}Repository already cloned${NC}"
    git pull origin master
fi

echo -e "${GREEN}Step 8: Creating environment file...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# GitHub Container Registry
GITHUB_REPOSITORY=YOUR_USERNAME/sogangcomputerclub.org
IMAGE_TAG=latest

# Database Configuration
POSTGRES_USER=memo_user
POSTGRES_PASSWORD=CHANGE_ME_USER_PASSWORD
POSTGRES_DB=memo_app
DATABASE_URL=postgresql+asyncpg://memo_user:CHANGE_ME_USER_PASSWORD@postgres:5432/memo_app

# Redis Configuration
REDIS_URL=redis://redis:6379

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka:9093

# Application Configuration
NODE_ENV=production
HOST=0.0.0.0
PORT=3000
EOF
    echo -e "${YELLOW}Environment file created. Please edit $DEPLOY_DIR/.env and set proper values${NC}"
    echo -e "${YELLOW}IMPORTANT: Change all passwords and update GITHUB_REPOSITORY${NC}"
else
    echo -e "${YELLOW}Environment file already exists${NC}"
fi

echo -e "${GREEN}Step 9: Setting up firewall...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw allow 22/tcp  # SSH
    sudo ufw allow 80/tcp  # HTTP
    sudo ufw allow 443/tcp # HTTPS
    echo -e "${GREEN}Firewall rules configured${NC}"
else
    echo -e "${YELLOW}UFW not found, skipping firewall setup${NC}"
fi

echo -e "${GREEN}Step 10: Generating SSH key for GitHub Actions...${NC}"
if [ ! -f "$HOME/.ssh/github_deploy" ]; then
    ssh-keygen -t ed25519 -C "github-actions-deploy" -f "$HOME/.ssh/github_deploy" -N ""
    echo -e "${GREEN}SSH key generated${NC}"
    echo -e "${YELLOW}Add this public key to authorized_keys:${NC}"
    cat "$HOME/.ssh/github_deploy.pub"
    echo ""
    cat "$HOME/.ssh/github_deploy.pub" >> "$HOME/.ssh/authorized_keys"
    echo -e "${GREEN}Public key added to authorized_keys${NC}"
    echo ""
    echo -e "${YELLOW}Copy this PRIVATE key to GitHub Secret PROD_SSH_KEY:${NC}"
    echo -e "${RED}(Keep this secure! Do not share publicly)${NC}"
    cat "$HOME/.ssh/github_deploy"
else
    echo -e "${YELLOW}SSH key already exists${NC}"
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Edit the .env file: ${YELLOW}nano $DEPLOY_DIR/.env${NC}"
echo -e "2. Update GitHub repository secrets with:"
echo -e "   - PROD_HOST: $(curl -s ifconfig.me)"
echo -e "   - PROD_USERNAME: $USER"
echo -e "   - PROD_SSH_KEY: (private key shown above)"
echo -e "   - PROD_SSH_PORT: 22"
echo -e "   - PROD_DEPLOY_PATH: $DEPLOY_DIR"
echo -e "3. Re-login to apply docker group: ${YELLOW}newgrp docker${NC}"
echo -e "4. Test deployment: ${YELLOW}cd $DEPLOY_DIR && docker-compose -f docker-compose.prod.yml pull${NC}"
echo ""
echo -e "${GREEN}Documentation: $DEPLOY_DIR/docs/DEPLOYMENT.md${NC}"
