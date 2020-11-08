#!/usr/bin/env bash

trap 'echo Stopping dev env...; kill $(jobs -p); wait; exit' SIGINT SIGTERM

export HLL_PASSWORD=<fill in yours>
export HLL_PORT=<fill in yours>
export HLL_HOST=<fill in yours>
export HLL_DB_PASSWORD=<fill in yours>
export DJANGO_DEBUG=True

export DB_URL=postgres://rcon:$HLL_DB_PASSWORD@localhost:5432
export REDIS_URL=redis://localhost:6379/0

docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d redis postgres

pip install -r requirements.txt
PYTHONPATH=$PWD DJANGO_DEBUG=$DJANGO_DEBUG ./rconweb/manage.py makemigrations; ./rconweb/manage.py migrate; ./rconweb/manage.py runserver &

cd rcongui/
npm install
npm start &

echo 'Press CTRL+C to quit'

wait