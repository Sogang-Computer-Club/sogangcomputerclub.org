#!/bin/sh
# SSL 인증서 확인
if [ ! -f /etc/nginx/certs/fullchain.pem ]; then
  echo "ERROR: SSL certificate not found at /etc/nginx/certs/fullchain.pem"
  echo "Place Cloudflare Origin Certificate in certs/ directory"
  exit 1
fi
rm -f /etc/nginx/conf.d/default.conf
nginx -c /etc/nginx/nginx.conf -g 'daemon off;'
