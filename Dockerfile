FROM ghcr.io/civicactions/pyction:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
ENV UV_PROJECT_ENVIRONMENT=/tmp/venv
ENV UV_CACHE_DIR=/tmp/uv-cache

RUN uv sync --no-dev

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000
USER nobody
ENTRYPOINT ["./entrypoint.sh"]