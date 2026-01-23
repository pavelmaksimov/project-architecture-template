FROM python:3.12-slim AS base

# uv Docs https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
# Install package manager 'uv' (astral)
COPY --from=ghcr.io/astral-sh/uv:0.5.18 /uv /uvx /bin/
# For run app.
ENV PATH="/app/.venv/bin:$PATH"

RUN useradd -ms /bin/bash app
USER app

WORKDIR /app
RUN mkdir /app/logs

COPY pyproject.toml uv.lock /app
RUN uv sync --frozen

COPY project/ /app/project


FROM base AS test

RUN uv sync --frozen --dev
COPY tests /app/tests
