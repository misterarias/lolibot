# syntax=docker/dockerfile:1

FROM python:3.11-slim
# System deps
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=2.1.3
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set workdir
WORKDIR /app

# Copy only pyproject.toml and poetry.lock for dependency caching
COPY pyproject.toml poetry.lock ./

# Install dependencies (no dev for production, add --with dev for dev)
RUN poetry install --no-interaction --no-root

# Copy the rest of the code
COPY app.py ./
COPY lolibot lolibot/
COPY README.md ./

# Install the app itself (editable mode)
RUN poetry install --no-interaction

# Version label for Docker image
LABEL version="1.1.0"

# Default entrypoint
ENTRYPOINT ["poetry", "run", "loli", "telegram"]