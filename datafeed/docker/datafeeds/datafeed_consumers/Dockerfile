#!/bin/bash
FROM node:alpine

WORKDIR /usr/src/app

RUN apk add --no-cache python3 py3-pip make g++

RUN npm install redis
RUN npm install websocket
ENV REDIS_URL='datafeeds-redis-do-user-15063471-0.c.db.ondigitalocean.com'
ENV REDIS_PASSWORD='AVNS_FLTYvrLh1YVC96siJlh'
ENV REDIS_PORT=25061
ENV REDIS_CHANNEL='liqs:binance'

COPY . .

ENTRYPOINT ["/bin/sh", "entrypoint.sh"]

