FROM python:3.12-slim

WORKDIR /code

ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV UV_COMPILE_BYTECODE=1

RUN apt-get update -y && \
    apt-get install -y cron logrotate git procps && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/code/.venv/bin:$PATH"

ENV PYTHONPATH=/code/
RUN chmod +x entrypoint.sh
RUN chmod +x manage.py
RUN chmod +x rconweb/manage.py
ENV LOGGING_FILENAME=startup.log

ENTRYPOINT [ "/code/entrypoint.sh" ]
