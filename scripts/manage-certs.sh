#!/bin/sh
set -e

# Domain and email
DOMAINS="-d sogangcomputerclub.org -d www.sogangcomputerclub.org"
EMAIL="sgccofficial2024@gmail.com"
WEBROOT="/var/www/html"

# Check if certificates exist
if [ ! -f /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem ]; then
  echo "Certificate not found. Requesting new certificate..."
  certbot certonly --webroot --webroot-path=$WEBROOT --email $EMAIL --agree-tos --no-eff-email --non-interactive $DOMAINS
else
  echo "Certificate found. Attempting renewal..."
  certbot renew
fi

# Copy certificates to output directory
# Use -L to follow symlinks since /etc/letsencrypt/live contains symlinks
echo "Copying certificates..."
cp -L /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem /output/certs/fullchain.pem
cp -L /etc/letsencrypt/live/sogangcomputerclub.org/privkey.pem /output/certs/privkey.pem

echo "Certificate operation complete."
