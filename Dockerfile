FROM python:3.11-slim

WORKDIR /code
RUN apt-get update -y && apt-get install -y cron logrotate git
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN pip install daphne
RUN pip install supervisor
COPY . .
ENV PYTHONPATH /code/
RUN chmod +x entrypoint.sh
RUN chmod +x manage.py
ENV LOGGING_FILENAME=startup.log

ENTRYPOINT [ "/code/entrypoint.sh" ]
