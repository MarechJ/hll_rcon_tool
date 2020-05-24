#!/usr/bin/env bash


python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@myproject.com', 'admin')" | python manage.py shell
gunicorn -w 4 -b 0.0.0.0 rconweb.wsgi