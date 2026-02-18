FROM python:3.11.7-slim-bookworm
USER root
RUN python -m pip install --upgrade pip "setuptools>=78.1.1" "wheel>=0.46.2"
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*


WORKDIR /app


RUN addgroup --system app && adduser --system --ingroup app app


ENV HOME=/home/app
RUN mkdir -p /home/app/.cache/pip && chown -R app:app /home/app


ARG REQUIREMENTS_FILE=requirements-prod.txt


COPY ${REQUIREMENTS_FILE} /app/requirements.txt
RUN python -m pip install --upgrade pip "setuptools>=78.1.1" "wheel>=0.46.2" \
    && python -m pip install --no-cache-dir -r /app/requirements.txt


COPY --chown=app:app app ./app

USER app

EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.main:app"]

