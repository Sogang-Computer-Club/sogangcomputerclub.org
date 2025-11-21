#!/bin/sh
apk add --no-cache openssl
if [ ! -f /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem ]; then
  mkdir -p /etc/letsencrypt/live/sogangcomputerclub.org && \
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/letsencrypt/live/sogangcomputerclub.org/privkey.pem -out /etc/letsencrypt/live/sogangcomputerclub.org/fullchain.pem -subj '/CN=sogangcomputerclub.org';
fi;
# Remove default nginx config that conflicts with our custom config
rm -f /etc/nginx/conf.d/default.conf
nginx -c /etc/nginx/nginx.conf -g 'daemon off;'