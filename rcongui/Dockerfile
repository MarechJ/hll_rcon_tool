FROM node:13-stretch

WORKDIR /code

RUN apt-get update -y && apt-get install -y nginx apache2-utils


RUN mkdir /pw

COPY package.json .
COPY package-lock.json .

RUN npm install

ENV REACT_APP_API_URL /api/

COPY src/ src/
COPY public/ public/
COPY entrypoint.sh .

RUN chmod +x /code/entrypoint.sh

RUN npm run build
COPY nginx.conf /etc/nginx/sites-available/default

RUN rm -rf src/
RUN rm -rf public/
RUN rm -rf node_modules/

WORKDIR /var/www

RUN mv /code/build /var/www/

ENTRYPOINT [ "/code/entrypoint.sh" ]
