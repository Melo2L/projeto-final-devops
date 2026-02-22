FROM python:3.11.7-slim-bookworm

# Reproducibility:
# - Pin base image tag (avoid floating '3.11-slim-bookworm')
# - Avoid 'apt-get upgrade/full-upgrade' inside the image; update by rebuilding with a newer base image

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app --home /home/app app
ENV HOME=/home/app
ENV PATH="/home/app/.local/bin:$PATH"

ARG REQUIREMENTS_FILE=requirements-prod.txt

COPY ${REQUIREMENTS_FILE} /app/requirements.txt
RUN python -m pip install --upgrade pip "setuptools>=78.1.1" "wheel>=0.46.2" \
 && pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=app:app app ./app

USER app
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.main:app"]
