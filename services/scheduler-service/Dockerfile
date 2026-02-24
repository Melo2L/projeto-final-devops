FROM python:3.11-alpine3.22@sha256:3f631db1a2b958674f293189d93e2fd697420172f8850514dd28176c8b86a45a

RUN apk update && apk upgrade --no-cache \
 && apk add --no-cache ca-certificates \
 && update-ca-certificates

RUN addgroup --system app && adduser --system --ingroup app --home /home/app app
ENV HOME=/home/app
ENV PATH="/home/app/.local/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip "setuptools>=78.1.1" "wheel>=0.46.2" \
 && pip install --no-cache-dir -r requirements.txt

COPY app ./app

USER app


CMD ["python", "app/main.py"]
