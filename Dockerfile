FROM python:3.11-slim

WORKDIR /code
RUN apt-get update -y && apt-get install -y cron logrotate git procps
COPY requirements.txt .
# Save Docker container disk space since the cache is useless there
# and don't generate .pyc
RUN pip install -r requirements.txt --no-compile --no-cache-dir
RUN pip install gunicorn daphne supervisor --no-compile --no-cache-dir
COPY . .
ENV PYTHONPATH /code/
RUN chmod +x entrypoint.sh
RUN chmod +x manage.py
RUN chmod +x rconweb/manage.py
ENV LOGGING_FILENAME=startup.log

ENTRYPOINT [ "/code/entrypoint.sh" ]
