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

# Copy game specific assets to nginx root
cp -R "/code/assets/$game/images/." /var/www/
cp -R "/code/assets/$game/rcongui/." /var/www/
cp -R "/code/assets/$game/images/." /var/www_public/
cp -R "/code/assets/$game/rcongui_public/." /var/www_public/

if [ ! -f "/certs/cert.crt" ] || [ ! -f "/certs/key.key" ]; then
    echo "No certificates found. Generating self signed"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /certs/key.key -out /certs/cert.crt -subj "/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Org/CN=$RCONWEB_EXTERNAL_ADDRESS" 
fi

nginx -g "daemon off;"
