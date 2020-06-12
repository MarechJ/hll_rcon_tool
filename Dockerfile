FROM python:3.8-slim-buster

WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY rcon rcon
COPY rconweb rconweb
COPY manage.py .
COPY entrypoint.sh .
ENV FLASK_APP rcon.connection
ENV PYTHONPATH /code/
RUN chmod +x entrypoint.sh
RUN chmod +x manage.py

ENTRYPOINT [ "/code/entrypoint.sh" ]
