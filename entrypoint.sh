#!/usr/bin/env bash

set -e
set -x 

env
# Only run the database migrations in the maintenance container
if [ "$1" == 'maintenance' ] 
then
  alembic upgrade head
  # Convert old stye player IDs to new style (md5 hash)
  # TODO: we can eventually remove this in a few releases once old installs have updated their game servers and CRCON
  # SERVER_NUMBER is mandatory and not otherwise set in the maintenance container; only want it to run once
  # LOGGING_PATH and LOGGING_FILENAME need to be passed to get it to log to the directory that is bind mounted
  SERVER_NUMBER=1 LOGGING_PATH=/logs/ LOGGING_FILENAME=startup.log python -m rcon.cli convert_win_player_ids
  cd rconweb 
  ./manage.py makemigrations --no-input
  ./manage.py migrate --noinput
  # Create this file after migrations which is how Docker determines the container is healthy
  touch maintenance-container-healthy
  # Keep the container running until it's explicitly created again
  sleep infinity
fi

# Check if we're in a backend container
if [ "$1" == 'web' ] 
then  
  # If the database password isn't set, bail early
  if [ "$HLL_DB_PASSWORD" == '' ] 
  then
      echo "HLL_DB_PASSWORD not set"
      exit 0
  fi
  if [ "$HLL_HOST" == '' ] 
  then
      exit 0
  fi

  python -m rcon.user_config.seed_db
  ./manage.py register_api
  cd rconweb 
  ./manage.py collectstatic --noinput
  # If DONT_SEED_ADMIN_USER is not set to any value
  if [[ -z "$DONT_SEED_ADMIN_USER" ]]
  then
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').first() else None" | python manage.py shell
  fi
  export LOGGING_FILENAME=api_$SERVER_NUMBER.log
  daphne -b 0.0.0.0 -p 8001 rconweb.asgi:application &
  # Successfully running gunicorn will create the pid file which is how Docker determines the container is healthy
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

