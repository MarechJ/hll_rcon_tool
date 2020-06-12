#!/usr/bin/env bash
  
if [ "$HLL_HOST" == '' ] 
then
    exit 0
fi

htpasswd -cb /pw/.htpasswd "$RCONWEB_USERNAME" "$RCONWEB_PASSWORD" && nginx -g "daemon off;"
