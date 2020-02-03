FROM python:3.8-slim-buster

WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY rcon rcon
COPY rconweb rconweb
ENV FLASK_APP rcon.connection
ENV HLL_HOST ''
ENV HLL_PORT ''
ENV HLL_PASSWORD ''
ENV PYTHONPATH /code/

CMD cd rconweb && gunicorn -w 8 -b 0.0.0.0 rconweb.wsgi