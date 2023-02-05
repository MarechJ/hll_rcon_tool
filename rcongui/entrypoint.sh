#!/usr/bin/env sh

export REACT_APP_VERSION=$(cat /code/tag_version)

if [ "$HLL_HOST" == '' ] 
then
    $echo "HLL_HOST is not set. stopping"
    exit 0
fi

if [ ! -f "/certs/cert.crt" ] || [ ! -f "/certs/key.key" ]; then
    echo "No certificates found. Generating self signed"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/key.key -out /certs/cert.crt -subj "/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Org/CN=$RCONWEB_EXTERNAL_ADDRESS" 
fi

nginx -g "daemon off;"
