#!/usr/bin/env bash

set -e
set -x 

env
if [ "$1" == 'web' ] 
then
  if [ "$HLL_DB_PASSWORD" == '' ] 
  then
      echo "HLL_DB_PASSWORD not set"
      exit 0
  fi
  if [ "$HLL_HOST" == '' ] 
  then
      exit 0
  fi
  alembic upgrade head
  python -m rcon.user_config.seed_db
  ./manage.py register_api
  cd rconweb 
  ./manage.py makemigrations --no-input
  ./manage.py migrate --noinput
  ./manage.py collectstatic --noinput
  # If DONT_SEED_ADMIN_USER is not set to any value
  if [[ -z "$DONT_SEED_ADMIN_USER" ]]
  then
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').first() else None" | python manage.py shell
  fi
  export LOGGING_FILENAME=api_$SERVER_NUMBER.log
  gunicorn --preload --pid gunicorn.pid -w $NB_API_WORKERS -k gthread --threads $NB_API_THREADS -t 120 -b 0.0.0.0 rconweb.wsgi
  cd ..
  ./manage.py unregister_api
else
if [ "$1" == 'debug' ] 
then
  tail -f manage.py
fi
if [ "$HLL_HOST" == '' ] 
then
    exit 0
fi
  sleep 10
  env >> /etc/environment
  export LOGGING_FILENAME=supervisor_$SERVER_NUMBER.log
  supervisord -c /config/supervisord_$SERVER_NUMBER.conf || supervisord -c /config/supervisord.conf
fi

