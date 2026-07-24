#!/bin/bash
# Find IP
count=1
date  >> /home/silentcinema/filmserver.log
while [ $count -le 20 ]; do
  sleep 2
  echo "Looking for IP" >> /home/silentcinema/filmserver.log
  ip="$(ifconfig|grep -E -o 'inet (192\.168|10\.10)\.[0-9]{1,3}\.[0-9]{1,3}'|grep -E -o '(192\.168|10\.10)\.[0-9]{1,3}\.[0-9]{1,3}')"
  echo 'cors_origins "'$ip':8008"'
  # Start Mercure
  if [ ${#ip} -lt 2 ]; then
    echo "No IP found" >> /home/silentcinema/filmserver.log
  else
    echo echo "IP found $ip" >> /home/silentcinema/filmserver.log
    echo echo "Starting Apache" >> /home/silentcinema/filmserver.log
    service httpd start &
    echo echo "Starting mercure" >> /home/silentcinema/filmserver.log
    docker run \
      -e SERVER_NAME=':8009' \
      -e MERCURE_PUBLISHER_JWT_KEY='!ChangeThisMercureHubJWTSecretKey!' \
      -e MERCURE_SUBSCRIBER_JWT_KEY='!ChangeThisMercureHubJWTSecretKey!' \
      -e DEBUG='debug' \
      -e MERCURE_EXTRA_DIRECTIVES='anonymous' \
      -e MERCURE_EXTRA_DIRECTIVES='cors_origins "http://'$ip':8008"' \
      -p 8009:8009 \
      dunglas/mercure caddy run --config /etc/caddy/dev.Caddyfile &
    count = 30
  fi
  ((count++))
done
