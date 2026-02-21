#!/bin/bash
# SSL Certificate Setup Script for SGCC
# Run this script on EC2 after DNS is configured

set -e

DOMAIN="${1:-sogangcomputerclub.org}"
EMAIL="${2:-admin@sogangcomputerclub.org}"

echo "=== SSL Certificate Setup for $DOMAIN ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Create webroot directory
mkdir -p /var/www/html

# Stop nginx temporarily if it's blocking port 80
cd /opt/sgcc
docker compose -f docker-compose.aws.yml stop nginx || true

echo "1. Obtaining SSL certificate from Let's Encrypt..."
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "2. Creating certificate directory..."
mkdir -p /opt/sgcc/certs

echo "3. Copying certificates..."
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/sgcc/certs/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/sgcc/certs/
chown -R ec2-user:ec2-user /opt/sgcc/certs

echo "4. Setting up auto-renewal..."
# Create renewal hook to copy certificates
cat > /etc/letsencrypt/renewal-hooks/deploy/sgcc-copy-certs.sh << 'EOF'
#!/bin/bash
cp /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem /opt/sgcc/certs/
cp /etc/letsencrypt/live/sogangcomputerclub.org/privkey.pem /opt/sgcc/certs/
chown -R ec2-user:ec2-user /opt/sgcc/certs
cd /opt/sgcc && docker compose -f docker-compose.aws.yml restart nginx
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/sgcc-copy-certs.sh

# Add cron job for renewal check
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet") | crontab -

echo "5. Restarting nginx..."
docker compose -f docker-compose.aws.yml up -d nginx

echo ""
echo "=== SSL Setup Complete ==="
echo ""
echo "Your site should now be accessible at:"
echo "  https://$DOMAIN"
echo "  https://www.$DOMAIN"
echo ""
echo "Certificates will auto-renew via certbot cron job."
