FROM python:3.12-slim-bullseye AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


RUN pip install poetry==1.8.3

# Configuring poetry
RUN poetry config virtualenvs.create false

WORKDIR /app

# Copying requirements of a project
COPY pyproject.toml poetry.lock ./


# Installing requirements
RUN poetry install --no-root --no-dev
# Removing gcc
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copying actuall application
COPY ./src ./src
#RUN poetry install --only main

COPY ./scripts /scripts

#CMD ["/scripts/start-dev.sh"]


# Development stage
FROM base AS dev

# Install development dependencies
RUN poetry install --no-root --with dev
RUN pip uninstall -y poetry


# Production stage
FROM base AS prod

# Install only production dependencies
RUN poetry install --no-root --only main
RUN pip uninstall -y poetry
