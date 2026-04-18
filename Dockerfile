FROM ghcr.io/civicactions/pyction:latest

WORKDIR /app

RUN groupadd -g 1001 app && useradd -m -u 1001 -g app app

COPY pyproject.toml uv.lock ./

ENV UV_PROJECT_ENVIRONMENT=/tmp/venv \
    UV_NO_CACHE=1

RUN uv sync --no-dev && chown -R app:app /tmp/venv

COPY . .
RUN chmod +x entrypoint.sh && chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
