#!/usr/bin/env bash

if [ $1 == 'web' ] 
then
  if [ "$HLL_HOST" == '' ] 
  then
      exit 0
  fi
  cd rconweb 
  ./manage.py migrate
  ./manage.py collectstatic --noinput
  echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').first() else None" | python manage.py shell
  gunicorn -w 8 -k eventlet -t 120 -b 0.0.0.0 rconweb.wsgi
else
  ./manage.py $*
  saved=$?
fi
if [ "$HLL_HOST" == '' ] 
then
    exit 0
fi
exit $saved