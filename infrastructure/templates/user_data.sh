#!/bin/bash
set -e

# Log all output
exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting EC2 initialization at $(date)"

# Variables from Terraform
AWS_REGION="${aws_region}"
ECR_REGISTRY="${ecr_registry}"
PROJECT_NAME="${project_name}"
DB_HOST="${db_host}"
DB_NAME="${db_name}"
SQS_QUEUE_URL="${sqs_queue_url}"
SECRET_ARN="${secret_arn}"

# Update system
dnf update -y

# Install Docker
dnf install -y docker
systemctl enable docker
systemctl start docker

# Install Docker Compose v2
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Install AWS CLI v2 (already installed on AL2023, but ensure latest)
dnf install -y awscli-2

# Install git
dnf install -y git

# Install certbot for SSL
dnf install -y certbot python3-certbot-nginx

# Add ec2-user to docker group
usermod -aG docker ec2-user

# Create application directory
mkdir -p /opt/sgcc
chown -R ec2-user:ec2-user /opt/sgcc

# Create docker network
docker network create sgcc-network || true

# Create environment file with secrets from Secrets Manager
cat > /opt/sgcc/fetch-secrets.sh << 'SCRIPT'
#!/bin/bash
SECRET_ARN="$1"
AWS_REGION="$2"
ENV_FILE="$3"

# Fetch secrets from Secrets Manager
SECRETS=$(aws secretsmanager get-secret-value --secret-id "$SECRET_ARN" --region "$AWS_REGION" --query 'SecretString' --output text)

# Parse JSON and write to .env file
echo "$SECRETS" | python3 -c "
import json, sys
secrets = json.load(sys.stdin)
for key, value in secrets.items():
    print(f'{key}={value}')
" > "$ENV_FILE"

chmod 600 "$ENV_FILE"
echo "Secrets written to $ENV_FILE"
SCRIPT
chmod +x /opt/sgcc/fetch-secrets.sh

# Create deployment script
cat > /opt/sgcc/deploy.sh << 'DEPLOY'
#!/bin/bash
set -e

cd /opt/sgcc

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Fetch latest secrets
./fetch-secrets.sh "$SECRET_ARN" "$AWS_REGION" .env

# Pull latest images
docker compose -f docker-compose.aws.yml pull

# Deploy with zero-downtime
docker compose -f docker-compose.aws.yml up -d --remove-orphans

# Cleanup old images
docker image prune -f

echo "Deployment completed at $(date)"
DEPLOY
chmod +x /opt/sgcc/deploy.sh

# Create systemd service for auto-start
cat > /etc/systemd/system/sgcc.service << 'SERVICE'
[Unit]
Description=SGCC Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/sgcc
ExecStart=/usr/bin/docker compose -f docker-compose.aws.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.aws.yml down

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable sgcc.service

# Export environment variables for deploy script
cat > /opt/sgcc/.deploy-env << EOF
export AWS_REGION=$AWS_REGION
export ECR_REGISTRY=$ECR_REGISTRY
export PROJECT_NAME=$PROJECT_NAME
export DB_HOST=$DB_HOST
export DB_NAME=$DB_NAME
export SQS_QUEUE_URL=$SQS_QUEUE_URL
export SECRET_ARN=$SECRET_ARN
EOF
chmod 600 /opt/sgcc/.deploy-env

# Set ownership
chown -R ec2-user:ec2-user /opt/sgcc

echo "EC2 initialization completed at $(date)"
echo "Run 'cd /opt/sgcc && source .deploy-env && ./deploy.sh' to deploy"
