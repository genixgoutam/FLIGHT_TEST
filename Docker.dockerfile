
# syntax=docker/dockerfile:1

# Use Python 3.10+ as specified in README
ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set Django environment
ENV DJANGO_SETTINGS_MODULE=FILGHT.settings

WORKDIR /app

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Download dependencies as a separate step for Docker caching
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to non-privileged user
USER appuser

# Copy the source code
COPY --chown=appuser:appuser . .

# Copy AI model and data files
COPY --chown=appuser:appuser flight_path_ai_project/ flight_path_ai_project/
COPY --chown=appuser:appuser airports_cleaned.json .
COPY --chown=appuser:appuser airports_locations.json .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run database migrations
RUN python manage.py migrate

# Expose the port Django runs on
EXPOSE 8000

# Run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

