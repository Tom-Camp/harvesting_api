FROM ghcr.io/civicactions/pyction:latest

WORKDIR /app

COPY pyproject.toml uv.lock ./
ENV UV_PROJECT_ENVIRONMENT=/tmp/venv
RUN uv sync --no-dev

COPY . .
RUN chmod +x entrypoint.sh

RUN useradd -m -u 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
