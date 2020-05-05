FROM node:13-stretch

WORKDIR /var/www

RUN apt-get update -y && apt-get install -y nginx apache2-utils
COPY nginx.conf /etc/nginx/sites-available/default

RUN mkdir /pw

COPY . .

RUN npm install

ENV REACT_APP_API_URL /api/

RUN npm run build

CMD bash -c 'htpasswd -cb /pw/.htpasswd "$RCONWEB_USERNAME" "$RCONWEB_PASSWORD" && nginx -g "daemon off;"'
