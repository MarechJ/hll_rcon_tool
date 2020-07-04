#!/usr/bin/env bash

if [ $1 == 'web' ] 
then
  if [ "$HLL_HOST" == '' ] 
  then
      exit 0
  fi
  cd rconweb 
  ./manage.py migrate
  ./manage.py collectstatic
  gunicorn -w 8 -b 0.0.0.0 rconweb.wsgi
else
  ./manage.py $*
  saved=$?
fi
if [ "$HLL_HOST" == '' ] 
then
    exit 0
fi
exit $saved