FROM python:3.11.7-slim-bookworm
USER root
RUN python -m pip install --upgrade pip "setuptools>=78.1.1" "wheel>=0.46.2"
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN addgroup --system app && adduser --system --ingroup app --home /home/app app
ENV HOME=/home/app
ENV PATH="/home/app/.local/bin:$PATH"

USER app


WORKDIR /app

RUN python -m pip install --upgrade pip "setuptools>=78.1.1" "wheel>=0.46.2"


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 5001

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5001", "app.main:app"]

