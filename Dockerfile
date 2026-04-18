FROM ghcr.io/civicactions/pyction:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
ENV UV_PROJECT_ENVIRONMENT=/tmp/venv
RUN uv sync --no-dev

COPY . .
RUN chmod +x entrypoint.sh

RUN groupadd -g 1001 app && useradd -m -u 1001 -g app app && chown -R app:app /app
USER app

ENV UV_CACHE_DIR=/tmp/uv-cache

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
