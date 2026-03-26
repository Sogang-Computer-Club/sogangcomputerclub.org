#!/bin/sh
# SSL 인증서가 없으면 자체 서명 인증서 생성
if [ ! -f /etc/nginx/certs/fullchain.pem ]; then
  apk add --no-cache openssl
  mkdir -p /etc/nginx/certs
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/certs/privkey.pem \
    -out /etc/nginx/certs/fullchain.pem \
    -subj '/CN=sogangcomputerclub.org'
fi
rm -f /etc/nginx/conf.d/default.conf
nginx -c /etc/nginx/nginx.conf -g 'daemon off;'
