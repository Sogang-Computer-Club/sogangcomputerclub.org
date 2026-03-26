#!/bin/sh
# network_mode: host 환경에서 nginx 대기 (127.0.0.1 사용)
while ! nc -z 127.0.0.1 80; do sleep 1; done

certbot certonly --webroot \
  --webroot-path=/var/www/html \
  --email sgccofficial2024@gmail.com \
  --agree-tos --no-eff-email --non-interactive --renew-by-default \
  -d sogangcomputerclub.org -d www.sogangcomputerclub.org

# 인증서를 nginx이 읽는 경로로 복사
CERT_DIR=$(find /etc/letsencrypt/live -type d -name "sogangcomputerclub.org*" | head -n 1)
if [ -n "$CERT_DIR" ]; then
  cp "$CERT_DIR/fullchain.pem" /etc/nginx/certs/fullchain.pem
  cp "$CERT_DIR/privkey.pem" /etc/nginx/certs/privkey.pem
  # nginx 리로드 (host network이므로 직접 시그널)
  kill -HUP $(cat /var/run/nginx.pid 2>/dev/null) 2>/dev/null || true
fi
