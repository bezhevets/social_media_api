FROM python:3.11-slim-buster
LABEL maintainer="begik4@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install -y libpq-dev gcc


RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN chown -R django-user:django-user /app/media
RUN chmod -R 755 /app/media

USER django-user
