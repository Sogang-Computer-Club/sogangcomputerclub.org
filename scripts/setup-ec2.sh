#!/bin/bash
# EC2 Setup Script for SGCC AWS Deployment
# Run this script on the EC2 instance after Terraform deployment

set -e

echo "=== SGCC EC2 Setup Script ==="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run as ec2-user, not root"
    exit 1
fi

# Check if required environment variables are set
if [ -z "$AWS_REGION" ] || [ -z "$ECR_REGISTRY" ] || [ -z "$SECRET_ARN" ]; then
    echo "Required environment variables not set."
    echo "Please run: source /opt/sgcc/.deploy-env"
    exit 1
fi

cd /opt/sgcc

echo "1. Copying configuration files from repository..."
# Assuming the repository is cloned
if [ -d "/tmp/sgcc-repo" ]; then
    mkdir -p deploy
    cp /tmp/sgcc-repo/deploy/docker-compose.aws.yml deploy/
    cp /tmp/sgcc-repo/nginx-aws.conf .
    cp /tmp/sgcc-repo/prometheus.yml .
    cp -r /tmp/sgcc-repo/grafana .
    echo "   Configuration files copied."
else
    echo "   Repository not found. Please clone it first:"
    echo "   git clone https://github.com/your-org/sogangcomputerclub.org.git /tmp/sgcc-repo"
    exit 1
fi

echo "2. Fetching secrets from AWS Secrets Manager..."
./fetch-secrets.sh "$SECRET_ARN" "$AWS_REGION" .env
echo "   Secrets fetched."

echo "3. Adding ECR configuration to .env..."
echo "ECR_REGISTRY=$ECR_REGISTRY" >> .env
echo "PROJECT_NAME=$PROJECT_NAME" >> .env
echo "IMAGE_TAG=latest" >> .env
echo "AWS_REGION=$AWS_REGION" >> .env
echo "   ECR configuration added."

echo "4. Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
echo "   ECR login successful."

echo "5. Creating SSL certificate directory..."
mkdir -p certs
echo "   Directory created. SSL certificates will be configured by certbot."

echo "6. Pulling Docker images..."
docker compose -f deploy/docker-compose.aws.yml pull
echo "   Images pulled."

echo "7. Starting services..."
docker compose -f deploy/docker-compose.aws.yml up -d
echo "   Services started."

echo "8. Waiting for services to be healthy..."
sleep 30

echo "9. Checking service status..."
docker compose -f deploy/docker-compose.aws.yml ps

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure DNS: Point sogangcomputerclub.org to $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "2. Configure SSL with certbot:"
echo "   sudo certbot certonly --webroot -w /var/www/html -d sogangcomputerclub.org -d www.sogangcomputerclub.org"
echo "3. Copy SSL certificates:"
echo "   sudo cp /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem /opt/sgcc/certs/"
echo "   sudo cp /etc/letsencrypt/live/sogangcomputerclub.org/privkey.pem /opt/sgcc/certs/"
echo "4. Restart nginx:"
echo "   docker compose -f deploy/docker-compose.aws.yml restart nginx"
echo ""
