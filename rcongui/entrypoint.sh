#!/usr/bin/env sh

export REACT_APP_VERSION=$(cat /code/tag_version)

game=${HLL_GAME:-hll}
case "$game" in
    hll|hllv) ;;
    *)
        echo "Unsupported HLL_GAME '$game'; expected 'hll' or 'hllv'" >&2
        exit 1
        ;;
esac

export HLL_GAME=${game}

# Vite environment variables are compiled into the bundle. Generate the
# deployment-specific values at container startup instead.
runtime_config="window.__CRCON_CONFIG__ = Object.freeze({ HLL_GAME: \"$game\" });"
printf '%s\n' "$runtime_config" > /var/www/runtime-config.js
printf '%s\n' "$runtime_config" > /var/www_public/runtime-config.js

# Copy game specific assets to nginx root
cp -R "/code/assets/$game/images/." /var/www/
cp -R "/code/assets/$game/rcongui/." /var/www/
cp -R "/code/assets/$game/images/." /var/www_public/
cp -R "/code/assets/$game/rcongui_public/." /var/www_public/

if [ ! -f "/certs/cert.crt" ] || [ ! -f "/certs/key.key" ]; then
    echo "No certificates found. Generating self signed"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/key.key -out /certs/cert.crt -subj "/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Org/CN=$RCONWEB_EXTERNAL_ADDRESS" 
fi

if [ -f "/config/nginx.conf" ]; then
    echo "nginx.conf found using it"
    cp /config/nginx.conf /etc/nginx/conf.d/default.conf
else
    echo "nginx.conf not found, falling back to default-nginx.conf"
    cp /config/default-nginx.conf /etc/nginx/conf.d/default.conf
fi

nginx -g "daemon off;"
