#!/bin/sh
apk add --no-cache docker-cli
while ! nc -z nginx 80; do sleep 1; done;
certbot certonly --webroot --webroot-path=/var/www/html --email sgccofficial2024@gmail.com --agree-tos --no-eff-email --non-interactive --renew-by-default -d sogangcomputerclub.org -d www.sogangcomputerclub.org;
CERT_DIR=$(find /etc/letsencrypt/live -type d -name "sogangcomputerclub.org-*" | head -n 1)
if [ -n "$CERT_DIR" ]; then
  mv $CERT_DIR/* /etc/letsencrypt/live/sogangcomputerclub.org/
fi
docker exec sogangcomputercluborg-nginx-1 nginx -s reload
