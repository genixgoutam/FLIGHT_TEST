# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=FILGHT.settings

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Install gunicorn (if not in requirements.txt)
RUN pip install gunicorn

USER appuser

COPY --chown=appuser:appuser . .

COPY --chown=appuser:appuser qaoa_angle_predictor.keras .
COPY --chown=appuser:appuser airports_cleaned.json .
COPY --chown=appuser:appuser airports_locations.json .

# Optional if using script
# COPY render-start.sh .
# RUN chmod +x render-start.sh
# CMD ["./render-start.sh"]

EXPOSE 8010

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
