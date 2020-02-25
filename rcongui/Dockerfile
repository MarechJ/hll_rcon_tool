FROM node:13-stretch

WORKDIR /var/www
VOLUME /node_cache
ARG REACT_APP_BATTLEMETRICS_SERVERID
ENV REACT_APP_BATTLEMETRICS_SERVERID=${REACT_APP_BATTLEMETRICS_SERVERID}
RUN apt-get update -y && apt-get install -y nginx
COPY nginx.conf /etc/nginx/sites-available/default

COPY . .

RUN npm install --production /node_cache
ENV REACT_APP_API_URL /api/

RUN npm run build

CMD nginx -g 'daemon off;'