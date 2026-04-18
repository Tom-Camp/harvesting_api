FROM ghcr.io/civicactions/pyction:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
ENV UV_PROJECT_ENVIRONMENT=/tmp/venv
ENV UV_NO_CACHE=1

RUN uv sync --no-dev

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
