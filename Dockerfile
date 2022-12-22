FROM python:3.9.15-alpine
RUN mkdir /usr/src/kuf_aero_bot
WORKDIR /usr/src/kuf_aero_bot
COPY . .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1

