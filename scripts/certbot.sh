#!/bin/sh
# nginx가 준비될 때까지 대기 (host 네트워크 사용)
while ! nc -z 127.0.0.1 80; do sleep 1; done;

# Let's Encrypt 인증서 발급
certbot certonly \
  --standalone \
  --preferred-challenges http \
  --email sgccofficial2024@gmail.com \
  --agree-tos --no-eff-email --non-interactive \
  -d sogangcomputerclub.org -d www.sogangcomputerclub.org

# 발급된 인증서를 nginx 마운트 경로로 복사
if [ -f /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem ]; then
  cp /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem /etc/nginx/certs/fullchain.pem
  cp /etc/letsencrypt/live/sogangcomputerclub.org/privkey.pem /etc/nginx/certs/privkey.pem
  echo "SSL certificates copied to /etc/nginx/certs/"
fi
