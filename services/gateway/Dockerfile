FROM python:3.11-alpine3.22@sha256:3f631db1a2b958674f293189d93e2fd697420172f8850514dd28176c8b86a45a

WORKDIR /app

RUN apk update && apk upgrade --no-cache \
 && apk add --no-cache ca-certificates \
 && update-ca-certificates

# Create non-root user
RUN addgroup -S app && adduser -S app -G app -h /home/app
ENV HOME=/home/app
ENV PATH="/home/app/.local/bin:$PATH"

ARG REQUIREMENTS_FILE=requirements-prod.txt
COPY ${REQUIREMENTS_FILE} /app/requirements.txt

RUN python -m pip install --upgrade pip "setuptools>=78.1.1" "wheel>=0.46.2" \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=app:app app /app/app

USER app
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.main:app"]