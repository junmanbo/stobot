# syntax=docker/dockerfile:1
FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache chromium-chromedriver

COPY . .

RUN mkdir /config

VOLUME /config

CMD [ "python", "./main.py" ]
