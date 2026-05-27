FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.8 /uv /usr/local/bin/uv

WORKDIR /opt/test-env
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

ENV PATH="/opt/test-env/.venv/bin:$PATH"

RUN playwright install --with-deps chromium

WORKDIR /tests
