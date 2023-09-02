#!/bin/bash
FROM --platform=linux/amd64 node:alpine

WORKDIR /usr/src/app

RUN npm install redis
RUN npm install websocket
RUN npm install @questdb/nodejs-client

COPY . .

CMD ["bash", "entrypoint.sh"]

