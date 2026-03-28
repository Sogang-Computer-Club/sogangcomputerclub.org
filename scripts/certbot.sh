#!/bin/sh
# Let's Encrypt 인증서 발급 (standalone 모드 — nginx 중지 상태에서 실행)
certbot certonly \
  --standalone \
  --email sgccofficial2024@gmail.com \
  --agree-tos --no-eff-email --non-interactive \
  -d sogangcomputerclub.org -d www.sogangcomputerclub.org

# 발급된 인증서를 nginx 마운트 경로로 복사
if [ -f /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem ]; then
  cp /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem /etc/nginx/certs/fullchain.pem
  cp /etc/letsencrypt/live/sogangcomputerclub.org/privkey.pem /etc/nginx/certs/privkey.pem
  echo "SSL certificates installed successfully."
else
  echo "Certificate issuance failed. Check logs: /var/log/letsencrypt/letsencrypt.log"
fi
