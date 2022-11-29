FROM python:3.9.15-alpine
RUN apk update \
    apk add \
    build-base \
    postgresql \
    postgresql-dev \
    libpq
RUN mkdir /usr/src/kuf-aero-bot
WORKDIR /usr/src/kuf-aero-bot
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY . .

