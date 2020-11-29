#!/usr/bin/env bash

set -e
set -x 

env
if [ "$1" == 'web' ] 
then
  if [ "$HLL_HOST" == '' ] 
  then
      exit 0
  fi
  cd rconweb 
  ./manage.py migrate --noinput
  ./manage.py collectstatic --noinput
  echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').first() else None" | python manage.py shell
  gunicorn -w 8 -t 120 -b 0.0.0.0 rconweb.wsgi
else
if [ "$HLL_HOST" == '' ] 
then
    exit 0
fi
  ./manage.py init_db
  supervisord
fi

