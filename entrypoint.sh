#!/usr/bin/env bash

if [ $1 == 'web' ] 
then
  cd rconweb 
  gunicorn -w 8 -b 0.0.0.0 rconweb.wsgi
  saved=$?
else
  ./manage.py $*
  saved=$?
fi
if [ "$HLL_HOST" == '' ] 
then
    exit 0
fi

exit $saved