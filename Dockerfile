FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

RUN chmod +x entrypoint.sh

RUN groupadd --system app && useradd --system --gid app --no-create-home --home /app app \
    && chown -R app:app /app

USER app

ENV HOME=/app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
