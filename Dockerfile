FROM python:3.11-buster

WORKDIR /code
RUN apt-get update -y && apt-get install -y cron logrotate
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN pip install gunicorn[eventlet]
RUN pip install supervisor
COPY . .
ENV FLASK_APP rcon.connection
ENV PYTHONPATH /code/
RUN chmod +x entrypoint.sh
RUN chmod +x manage.py
ENV LOGGING_FILENAME=startup.log

ENTRYPOINT [ "/code/entrypoint.sh" ]
