#!/usr/bin/env sh

REACT_APP_VERSION=$(cat /code/tag_version)
export REACT_APP_VERSION

game=${HLL_GAME:-hll}
case "$game" in
    hll|hllv) ;;
    *)
        echo "Unsupported HLL_GAME '$game'; expected 'hll' or 'hllv'" >&2
        exit 1
        ;;
esac

export HLL_GAME="${game}"

# Vite environment variables are compiled into the bundle. Generate the
# deployment-specific values at container startup instead.
runtime_config="window.__CRCON_CONFIG__ = Object.freeze({ HLL_GAME: \"$game\" });"
printf '%s\n' "$runtime_config" > /var/www/runtime-config.js
printf '%s\n' "$runtime_config" > /var/www_public/runtime-config.js

# Link game specific assets to nginx root
cp -Rs "/code/assets/$game/images/." /var/www/
cp -Rs "/code/assets/$game/rcongui/." /var/www/
cp -Rs "/code/assets/$game/images/." /var/www_public/
cp -Rs "/code/assets/$game/rcongui_public/." /var/www_public/

if [ ! -f "/certs/cert.crt" ] || [ ! -f "/certs/key.key" ]; then
    echo "No certificates found. Generating self signed"
    openssl ecparam -name secp384r1 -genkey -noout -out /certs/key.key
    openssl req -x509 -nodes -days 365 -key /certs/key.key -out /certs/cert.crt \
        -subj "/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Org/CN=$RCONWEB_EXTERNAL_ADDRESS" \
        -sha256
fi

if [ -f "/config/nginx.conf" ]; then
    echo "nginx.conf found using it"
    cp /config/nginx.conf /etc/nginx/conf.d/default.conf
else
    echo "nginx.conf not found, falling back to default-nginx.conf"
    cp /config/default-nginx.conf /etc/nginx/conf.d/default.conf
fi

exec nginx -g "daemon off;"
